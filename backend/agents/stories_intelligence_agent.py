"""
Stories Intelligence Agent.

Scansione proattiva delle Instagram Stories dei dealer seguiti usando GPT-4o Vision.
Non OCR — analisi visiva diretta: ogni story viene inviata a GPT-4o che estrae
brand, modello, referenza, prezzo, condizione e confidence.

Architettura:
  - Scheduler ogni 4-6h (indipendente dalle ricerche)
  - Risultati pre-indicizzati in SQLite (tabella dealer_listings)
  - Ricerca per referenza in O(1) — nessuna chiamata AI durante la ricerca

Flusso:
  1. cl.get_reels_tray_feed() → account con stories attive
  2. Per ogni account: cl.user_stories(pk) → lista story object
  3. Scarica thumbnail → base64 → GPT-4o Vision
  4. Estrae lista listing → upsert in dealer_listings
  5. Stories scadono in 24h — expires_at gestito nel DB
"""

import asyncio
import base64
import json
import sqlite3
import httpx
from datetime import datetime, timedelta, timezone
from pathlib import Path
from utils.logger import get_logger
from config import get_settings

logger = get_logger("stories_intelligence")

DB_PATH = Path(__file__).parent.parent / "data" / "resellers.db"

SCAN_INTERVAL_HOURS = 5  # ogni 5 ore


# ── DB init ──────────────────────────────────────────────────────────────────

def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_dealer_listings_table():
    """Crea la tabella dealer_listings se non esiste."""
    conn = _connect()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dealer_listings (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                dealer_username TEXT    NOT NULL,
                source          TEXT    NOT NULL DEFAULT 'instagram_story',
                brand           TEXT,
                model           TEXT,
                reference_raw   TEXT,
                reference_norm  TEXT,
                price           REAL,
                currency        TEXT    DEFAULT 'EUR',
                condition       TEXT,
                confidence      REAL    NOT NULL DEFAULT 0.0,
                story_id        TEXT,
                story_url       TEXT,
                image_url       TEXT,
                raw_gpt_json    TEXT,
                scraped_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at      TIMESTAMP,
                UNIQUE(dealer_username, story_id)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reference_norm
            ON dealer_listings(reference_norm)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at
            ON dealer_listings(expires_at)
        """)
    conn.close()
    logger.debug("dealer_listings table ready")


# ── GPT-4o Vision ─────────────────────────────────────────────────────────────

VISION_PROMPT = """This is an Instagram story posted by a professional watch dealer with a VAT number.
Your task is to extract ALL watch listings visible in this image.

Return ONLY valid JSON — no markdown, no explanation — with this exact structure:
{
  "listings": [
    {
      "brand": "Rolex",
      "model": "Submariner Date",
      "reference": "116610LN",
      "price": 14500,
      "currency": "EUR",
      "condition": "mint",
      "confidence": 0.92
    }
  ]
}

Rules:
- brand: watch manufacturer (Rolex, Patek Philippe, Audemars Piguet, Omega, Tudor, IWC, etc.)
- model: commercial name (Submariner, Nautilus, Royal Oak, etc.)
- reference: alphanumeric reference code visible in image or caption (null if not visible)
- price: numeric only, no symbols (null if not visible)
- currency: EUR, USD, GBP, CHF — infer from context (default EUR)
- condition: "mint", "excellent", "good", "fair", or "unknown"
- confidence: 0.0 to 1.0 — how sure you are this is a real watch listing

If no watches are for sale, return: {"listings": []}
"""


async def _analyze_story_with_vision(
    image_bytes: bytes,
    dealer_username: str,
    openai_api_key: str,
    openai_model: str = "gpt-4o",
) -> list[dict]:
    """Invia immagine a GPT-4o Vision, restituisce lista di listing estratti."""
    b64 = base64.b64encode(image_bytes).decode()
    data_url = f"data:image/jpeg;base64,{b64}"

    async with httpx.AsyncClient(timeout=45) as client:
        try:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": openai_model,
                    "max_tokens": 800,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": VISION_PROMPT},
                                {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                            ],
                        }
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(raw)
            listings = parsed.get("listings", [])
            logger.debug(f"  @{dealer_username} — GPT-4o: {len(listings)} listing trovati")
            return listings
        except json.JSONDecodeError as e:
            logger.warning(f"  @{dealer_username} — JSON parse error: {e}")
            return []
        except httpx.HTTPStatusError as e:
            logger.warning(f"  @{dealer_username} — OpenAI API error {e.response.status_code}")
            return []
        except Exception as e:
            logger.warning(f"  @{dealer_username} — vision error: {e}")
            return []


async def _download_image(url: str) -> bytes | None:
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.content
    except Exception as e:
        logger.debug(f"Download error {url}: {e}")
    return None


def _normalize_reference(ref: str | None) -> str | None:
    """Normalizza referenza: uppercase, rimuove spazi e caratteri non alfanumerici."""
    if not ref:
        return None
    return ref.upper().replace(" ", "").replace("/", "").replace("-", "")


# ── DB writes ─────────────────────────────────────────────────────────────────

def _upsert_listings(
    dealer_username: str,
    story_id: str,
    story_url: str | None,
    image_url: str | None,
    listings: list[dict],
    raw_gpt_json: str,
):
    """Inserisce o aggiorna i listing nel DB. Stories scadono dopo 24h."""
    if not listings:
        return
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    conn = _connect()
    inserted = 0
    with conn:
        for lst in listings:
            confidence = float(lst.get("confidence", 0.0))
            if confidence < 0.5:
                continue  # skip low-confidence
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO dealer_listings
                        (dealer_username, source, brand, model, reference_raw,
                         reference_norm, price, currency, condition, confidence,
                         story_id, story_url, image_url, raw_gpt_json, expires_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        dealer_username,
                        "instagram_story",
                        lst.get("brand"),
                        lst.get("model"),
                        lst.get("reference"),
                        _normalize_reference(lst.get("reference")),
                        lst.get("price"),
                        lst.get("currency", "EUR"),
                        lst.get("condition", "unknown"),
                        confidence,
                        story_id,
                        story_url,
                        image_url,
                        raw_gpt_json,
                        expires_at,
                    ),
                )
                inserted += 1
            except Exception as e:
                logger.debug(f"  DB insert error: {e}")
    conn.close()
    if inserted:
        logger.info(f"  @{dealer_username} — salvati {inserted} listing")


# ── Search interface ──────────────────────────────────────────────────────────

def get_listings_for_reference(reference: str, min_confidence: float = 0.6) -> list[dict]:
    """
    Cerca nella tabella pre-indicizzata per referenza.
    Ritorna solo listing non scaduti con confidence sufficiente.
    """
    norm = _normalize_reference(reference)
    if not norm:
        return []

    conn = _connect()
    now = datetime.now(timezone.utc).isoformat()
    rows = conn.execute(
        """
        SELECT dealer_username, brand, model, reference_raw, price, currency,
               condition, confidence, story_url, image_url, scraped_at
        FROM dealer_listings
        WHERE (reference_norm = ? OR reference_raw LIKE ?)
          AND confidence >= ?
          AND (expires_at IS NULL OR expires_at > ?)
        ORDER BY confidence DESC, scraped_at DESC
        """,
        (norm, f"%{reference}%", min_confidence, now),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_listings(limit: int = 50, min_confidence: float = 0.6) -> list[dict]:
    """Ultimi listing non scaduti — per homepage o feed."""
    conn = _connect()
    now = datetime.now(timezone.utc).isoformat()
    rows = conn.execute(
        """
        SELECT dealer_username, brand, model, reference_raw, price, currency,
               condition, confidence, story_url, image_url, scraped_at
        FROM dealer_listings
        WHERE confidence >= ?
          AND (expires_at IS NULL OR expires_at > ?)
        ORDER BY scraped_at DESC
        LIMIT ?
        """,
        (min_confidence, now, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cleanup_expired_listings():
    """Rimuove listing scaduti (> 24h). Da chiamare periodicamente."""
    conn = _connect()
    now = datetime.now(timezone.utc).isoformat()
    with conn:
        deleted = conn.execute(
            "DELETE FROM dealer_listings WHERE expires_at IS NOT NULL AND expires_at < ?",
            (now,),
        ).rowcount
    conn.close()
    if deleted:
        logger.info(f"Cleanup: rimossi {deleted} listing scaduti")


# ── Main scanner ──────────────────────────────────────────────────────────────

def _get_tray_items(cl) -> list:
    """
    Ottieni account con stories attive.
    Prima prova il tray feed (una sola chiamata), poi fallback ai following.
    """
    try:
        tray = cl.get_reels_tray_feed()
        items = tray.get("tray", [])
        if items:
            logger.info(f"[stories] Tray: {len(items)} account con stories attive")
            return items
    except Exception as e:
        logger.warning(f"[stories] Tray non disponibile ({type(e).__name__}), uso following come fallback")

    # Fallback: itera i following e prova a caricare le stories di ciascuno
    try:
        settings = get_settings()
        user_info = cl.user_info_by_username(settings.instagram_username)
        following = cl.user_following(int(user_info.pk), amount=200)
        logger.info(f"[stories] Fallback following: {len(following)} account da controllare")
        # Costruisce struttura compatibile con tray_items
        return [
            {"user": {"username": u.username, "pk": str(u.pk)}, "id": str(u.pk)}
            for u in following.values()
            if hasattr(u, "username")
        ]
    except Exception as e:
        logger.warning(f"[stories] Fallback following error: {e}")
        return []


async def run_full_stories_scan(cl) -> int:
    """
    Scansiona tutte le stories degli account seguiti dall'account Watch Scanner.

    Args:
        cl: istanza instagrapi.Client già autenticata.

    Returns:
        Numero totale di listing estratti.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY non configurata — stories scan disabilitato")
        return 0

    init_dealer_listings_table()

    tray_items = _get_tray_items(cl)
    if not tray_items:
        logger.warning("[stories] Nessun account trovato — scan annullato")
        return 0

    total_listings = 0
    scanned_accounts = 0

    for item in tray_items:
        user = item.get("user", {})
        username = user.get("username", "")
        user_id = user.get("pk") or item.get("id")
        if not user_id or not username:
            continue

        try:
            stories = cl.user_stories(int(user_id))
            if not stories:
                continue

            logger.info(f"[stories] @{username}: {len(stories)} stories")
            scanned_accounts += 1

            for story in stories:
                story_id = str(getattr(story, "pk", "") or getattr(story, "id", ""))
                if not story_id:
                    continue

                # Thumbnail URL
                img_url = None
                if hasattr(story, "thumbnail_url") and story.thumbnail_url:
                    img_url = str(story.thumbnail_url)
                elif hasattr(story, "video_url") and story.video_url:
                    img_url = str(story.video_url)

                if not img_url:
                    continue

                # Download
                image_bytes = await _download_image(img_url)
                if not image_bytes or len(image_bytes) < 1000:
                    continue

                # GPT-4o Vision
                listings = await _analyze_story_with_vision(
                    image_bytes,
                    username,
                    settings.openai_api_key,
                    settings.openai_model,
                )

                if listings:
                    story_url = f"https://www.instagram.com/{username}/"
                    raw_json = json.dumps(listings)
                    _upsert_listings(username, story_id, story_url, img_url, listings, raw_json)
                    total_listings += len(listings)

                # Rate limiting — rispetta Instagram
                await asyncio.sleep(1.5)

        except Exception as e:
            err = str(e).lower()
            if "challenge" in err or "loginrequired" in err.replace("_", ""):
                logger.warning(f"[stories] @{username} — challenge/auth error, stop scan")
                break
            logger.debug(f"[stories] @{username} — error: {e}")
            continue

        await asyncio.sleep(2)

    cleanup_expired_listings()

    logger.info(
        f"[stories] Scan completato — {scanned_accounts} account, "
        f"{total_listings} listing estratti"
    )
    return total_listings


# ── Scheduler ─────────────────────────────────────────────────────────────────

async def start_stories_intelligence_scheduler(instagram_username: str, instagram_password: str):
    """
    Background task: scansiona le stories ogni SCAN_INTERVAL_HOURS ore.
    Da lanciare all'avvio di FastAPI tramite lifespan.
    """
    from scrapers.instagram import get_client

    logger.info(f"[stories] Scheduler avviato (ogni {SCAN_INTERVAL_HOURS}h)")

    # Prima scansione dopo 60s dall'avvio (lascia tempo all'app di partire)
    await asyncio.sleep(60)

    while True:
        try:
            logger.info("[stories] Avvio scansione periodica...")
            cl = get_client(instagram_username, instagram_password)
            if cl:
                count = await run_full_stories_scan(cl)
                logger.info(f"[stories] Scansione completata — {count} listing totali")
            else:
                logger.warning("[stories] Login Instagram fallito — retry al prossimo ciclo")
        except Exception as e:
            logger.error(f"[stories] Errore scheduler: {e}")

        await asyncio.sleep(SCAN_INTERVAL_HOURS * 3600)
