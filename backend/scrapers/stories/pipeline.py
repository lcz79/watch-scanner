"""
Pipeline principale Instagram Stories.
Coordina capture (Playwright) → Vision AI (GPT-4o) → storage.

Playwright = browser reale → nessun ban Meta.
GPT-4o Vision = analisi precisa, niente OCR impreciso.
Fallback OCR se OPENAI_API_KEY non configurata.

Account target: dealer dal DB discovery + PRIORITY_DEALERS statici.
"""
import asyncio
import base64
import json
import random
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger
from models.schemas import WatchListing
from scrapers.stories.capture import (
    PRIORITY_DEALERS, capture_stories, capture_recent_posts, has_valid_auth,
)
from scrapers.stories.ocr import parse_frame
from scrapers.stories.storage import save_listing, get_stories_for_reference

logger = get_logger("stories.pipeline")

# Configurazione run
MAX_ACCOUNTS_PER_RUN = 30        # con Vision AI possiamo essere più ambiziosi
INTER_ACCOUNT_DELAY = (8, 18)   # secondi tra un account e l'altro
MIN_CONFIDENCE = 0.50            # Vision AI è più precisa, alziamo la soglia


def _get_dealer_accounts() -> list[str]:
    """
    Ritorna la lista di account da scansionare.
    Priorità: dealer dal DB discovery → PRIORITY_DEALERS statici.
    """
    try:
        from agents.discovery.resellers_db import get_all_resellers
        db_dealers = [r["username"] for r in get_all_resellers(min_score=3, platform="instagram")]
        if db_dealers:
            combined = list(dict.fromkeys(PRIORITY_DEALERS + db_dealers))  # dedup, ordine preservato
            logger.debug(f"Account target: {len(combined)} ({len(db_dealers)} dal DB + {len(PRIORITY_DEALERS)} statici)")
            return combined
    except Exception as e:
        logger.debug(f"DB resellers non disponibile: {e}")
    return list(PRIORITY_DEALERS)


async def _analyze_frame_with_vision(screenshot_path: str, username: str) -> list[dict]:
    """
    Invia lo screenshot a GPT-4o Vision.
    Ritorna lista di listing (stessa struttura di _analyze_story_with_vision).
    """
    from config import get_settings
    settings = get_settings()
    if not settings.openai_api_key:
        return []

    import httpx
    from agents.stories_intelligence_agent import VISION_PROMPT

    path = Path(screenshot_path)
    if not path.exists():
        return []

    b64 = base64.b64encode(path.read_bytes()).decode()
    data_url = f"data:image/png;base64,{b64}"

    async with httpx.AsyncClient(timeout=45) as client:
        try:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openai_model,
                    "max_tokens": 800,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": VISION_PROMPT},
                            {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                        ],
                    }],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            return json.loads(raw).get("listings", [])
        except Exception as e:
            logger.debug(f"  @{username} Vision error: {e}")
            return []


async def process_account(username: str) -> list[dict]:
    """
    Processa un singolo account dealer:
      1. Playwright cattura screenshot delle stories (browser reale → nessun ban)
      2. GPT-4o Vision analizza ogni screenshot (se OPENAI_API_KEY presente)
         oppure OCR come fallback
      3. Salva in dealer_listings (stories_intelligence_agent) + storage locale
    """
    from config import get_settings
    settings = get_settings()
    use_vision = bool(settings.openai_api_key)

    results = []

    # Skip dealer opt-out
    try:
        from agents.stories_intelligence_agent import _is_opted_out
        if _is_opted_out(username):
            logger.debug(f"@{username}: opt-out — skip")
            return []
    except Exception:
        pass

    # Cattura Playwright (browser reale, cookie session salvata)
    frames = await capture_stories(username, max_frames=15)
    if not frames:
        logger.debug(f"@{username}: nessuna story — fallback post recenti")
        frames = await capture_recent_posts(username, max_posts=6)
    if not frames:
        return []

    logger.info(f"@{username}: {len(frames)} frame catturati — analisi {'Vision AI' if use_vision else 'OCR'}")

    for frame in frames:
        screenshot_path = frame.get("screenshot_path", "")
        frame_idx = frame.get("frame_index", 0)
        story_id = f"{username}_{frame['timestamp']}_{frame_idx}"

        if use_vision:
            # ── GPT-4o Vision ──────────────────────────────────────────────
            vision_listings = await _analyze_frame_with_vision(screenshot_path, username)
            for lst in vision_listings:
                confidence = float(lst.get("confidence", 0))
                if confidence < MIN_CONFIDENCE:
                    continue
                parsed = {
                    "username": username,
                    "frame_index": frame_idx,
                    "screenshot_path": screenshot_path,
                    "timestamp": frame["timestamp"],
                    "post_url": frame.get("post_url", f"https://www.instagram.com/{username}/"),
                    "brand": lst.get("brand"),
                    "model": lst.get("model"),
                    "reference": lst.get("reference"),
                    "price": lst.get("price"),
                    "currency": lst.get("currency", "EUR"),
                    "condition": lst.get("condition", "unknown"),
                    "confidence": confidence,
                    "availability": "available",
                    "text_raw": frame.get("raw_page_text", "")[:300],
                }
                # Persisti in dealer_listings
                try:
                    from agents.stories_intelligence_agent import _upsert_listings
                    _upsert_listings(
                        username, story_id,
                        parsed["post_url"], screenshot_path,
                        [lst], json.dumps([lst]),
                    )
                except Exception as e:
                    logger.debug(f"  upsert_listings error: {e}")
                save_listing(parsed)
                results.append(parsed)
                logger.debug(f"@{username} frame {frame_idx}: {lst.get('brand')} {lst.get('reference')} {lst.get('price')}€ conf={confidence:.2f}")
        else:
            # ── Fallback OCR ───────────────────────────────────────────────
            parsed = parse_frame(
                screenshot_path=screenshot_path,
                raw_page_text=frame.get("raw_page_text", ""),
                username=username,
                timestamp=frame["timestamp"],
                post_url=frame.get("post_url", ""),
            )
            if not parsed or parsed.get("confidence", 0) < MIN_CONFIDENCE:
                continue
            if parsed.get("availability") in ("sold", "reserved"):
                continue
            save_listing(parsed)
            results.append(parsed)

    logger.info(f"@{username}: {len(results)} listing estratti")
    return results


async def run_stories_pipeline(
    accounts: list[str] | None = None,
    max_accounts: int = MAX_ACCOUNTS_PER_RUN,
) -> list[dict]:
    """
    Esegue la pipeline su tutti gli account (o quelli specificati).
    Ritorna tutti i listing trovati in questo run.
    """
    if not has_valid_auth():
        logger.warning(
            "Nessun auth state browser. "
            "Chiama POST /stories/setup con username+password per inizializzare."
        )
        return []

    target_accounts = list(accounts or _get_dealer_accounts())
    # Shuffle: non colpire sempre gli stessi account per primi
    random.shuffle(target_accounts)
    target_accounts = target_accounts[:max_accounts]

    all_results: list[dict] = []
    logger.info(f"Stories pipeline: {len(target_accounts)} account da processare")

    for username in target_accounts:
        try:
            results = await process_account(username)
            all_results.extend(results)
        except Exception as e:
            logger.debug(f"@{username} pipeline error: {e}")

        # Ritardo umano tra account
        delay = random.uniform(*INTER_ACCOUNT_DELAY)
        logger.debug(f"Pausa {delay:.1f}s prima del prossimo account...")
        await asyncio.sleep(delay)

    logger.info(f"Stories pipeline completata: {len(all_results)} listing totali")
    return all_results


def stories_to_watch_listings(stories: list[dict], reference: str) -> list[WatchListing]:
    """
    Converte i record story in WatchListing per l'orchestratore principale.
    Filtra per referenza se specificata; supporta i nuovi campi availability e currency.
    """
    listings: list[WatchListing] = []
    ref_clean = reference.replace(" ", "").upper()

    for s in stories:
        # Filtra per referenza
        story_ref = (s.get("reference") or "").replace(" ", "").upper()
        story_text = (s.get("text_raw") or "").upper()
        if ref_clean and ref_clean not in story_ref and ref_clean not in story_text:
            continue

        # Skip sold/reserved se il campo è presente (nuovi record)
        if s.get("availability") in ("sold", "reserved"):
            continue

        try:
            ts = datetime.fromisoformat(s["captured_at"].replace("Z", "+00:00"))
            ts = ts.replace(tzinfo=None)
        except Exception:
            ts = datetime.now()

        # Costruisci descrizione ricca con i nuovi campi
        desc_parts = [s.get("text_raw", "")[:150]]
        if s.get("contact"):
            desc_parts.append(f"Contatto: {s['contact']}")
        if s.get("has_full_set"):
            desc_parts.append("Full set")
        elif s.get("has_no_papers"):
            desc_parts.append("Solo orologio")

        listings.append(WatchListing(
            source="instagram_story",
            reference=reference,
            price=s["price"],
            currency=s.get("currency", "EUR"),
            seller=f"@{s['username']}",
            url=s.get("post_url") or f"https://www.instagram.com/{s['username']}/",
            condition=s.get("condition", "unknown"),
            scraped_at=ts,
            description=" | ".join(filter(None, desc_parts))[:300],
            image_url=None,
        ))

    return listings


async def get_stories_listings(reference: str) -> list[WatchListing]:
    """
    Entry point per l'agente: recupera dal DB le stories recenti per una referenza.
    La pipeline gira in background ogni 2.5h — qui leggiamo solo dal DB.
    """
    stories = get_stories_for_reference(reference, hours=48)
    return stories_to_watch_listings(stories, reference)


# ── Scheduler background ───────────────────────────────────────────────────────

# Orari fissi di scansione (ora locale italiana)
# 8:00 — dealer aprono, prima occhiata alle stories notturne
# 12:00 — pausa pranzo, picco di post
# 16:00 — pomeriggio, nuove stories business
# 19:00 — chiusura giornata lavorativa, ultime stories del giorno
SCAN_TIMES = [(8, 0), (12, 0), (16, 0), (19, 0)]


def _seconds_until_next_scan() -> float:
    """Calcola i secondi fino al prossimo orario di scansione pianificato."""
    from datetime import datetime as _dt
    now = _dt.now()
    today_slots = [
        now.replace(hour=h, minute=m, second=0, microsecond=0)
        for h, m in SCAN_TIMES
    ]
    # Prossimo slot nel giorno corrente
    future = [t for t in today_slots if t > now]
    if future:
        next_scan = future[0]
    else:
        # Nessun slot rimasto oggi — primo slot di domani
        tomorrow = now.replace(hour=SCAN_TIMES[0][0], minute=SCAN_TIMES[0][1],
                                second=0, microsecond=0)
        next_scan = tomorrow.replace(day=tomorrow.day + 1)  # semplice +1 giorno
        # gestione fine mese via timedelta
        from datetime import timedelta
        next_scan = (now + timedelta(days=1)).replace(
            hour=SCAN_TIMES[0][0], minute=SCAN_TIMES[0][1], second=0, microsecond=0
        )
    delta = (next_scan - now).total_seconds()
    logger.info(f"Prossima scansione stories: {next_scan.strftime('%H:%M')} (tra {delta/3600:.1f}h)")
    return delta


async def start_stories_scheduler_playwright():
    """
    Background scheduler a orari fissi: 08:00, 12:00, 16:00, 19:00 (ora italiana).
    Molto più efficiente dell'intervallo fisso — scansiona solo quando i dealer sono attivi.
    """
    slots_str = ", ".join(f"{h:02d}:{m:02d}" for h, m in SCAN_TIMES)
    logger.info(f"Stories scheduler (Playwright) avviato — scansioni alle {slots_str}")

    while True:
        wait = _seconds_until_next_scan()
        await asyncio.sleep(wait)
        try:
            logger.info("Stories scheduler: avvio run pianificato...")
            results = await run_stories_pipeline()
            logger.info(f"Stories scheduler: {len(results)} nuovi listing")
        except Exception as e:
            logger.warning(f"Stories scheduler error: {e}")
