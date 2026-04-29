# NOTE: il nuovo sistema Playwright è in scrapers/stories/pipeline.py
# Questo file mantiene la compatibilità con il SocialAgent (instagrapi).
# Per il nuovo pipeline basato su browser, vedi scrapers/stories/
"""
Instagram Stories Scanner.

Usa il reels tray per ottenere tutti gli account con stories attive in una sola
chiamata, poi carica le stories per ciascun account e usa OCR per trovare
referenze e prezzi.

Richiede: tesseract (brew install tesseract) + pytesseract + pillow + httpx
"""

import re
import asyncio
import httpx
from datetime import datetime, timezone
from models.schemas import WatchListing
from utils.logger import get_logger

logger = get_logger("scraper.instagram_stories")

PRICE_RE = re.compile(
    r'(?:prezzo|price|vendesi|vendo|asking|sale)\s*[:\-]?\s*[€$]?\s*([\d\.,]+)'
    r'|[€$]\s*([\d\.,]+)'
    r'|([\d\.]+[,\d]*)\s*[€$]'
    r'|([\d\.]+)\s*euro',
    re.IGNORECASE,
)


def _parse_price(text: str) -> float | None:
    for m in PRICE_RE.finditer(text):
        raw = next((g for g in m.groups() if g), None)
        if not raw:
            continue
        raw = raw.replace('.', '').replace(',', '.')
        try:
            price = float(raw)
            if 200 < price < 500_000:
                return price
        except ValueError:
            continue
    return None


def _ocr_image(image_bytes: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img, lang='ita+eng', config='--psm 11')
        return text
    except Exception as e:
        logger.debug(f"OCR error: {e}")
        return ""


async def _download_image(url: str) -> bytes | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, follow_redirects=True)
            if r.status_code == 200:
                return r.content
    except Exception as e:
        logger.debug(f"Download error: {e}")
    return None


async def _ocr_story(story, username: str, reference: str, ref_clean: str) -> WatchListing | None:
    """Scarica thumbnail di una story, OCR, filtra per referenza e prezzo."""
    img_url = str(story.thumbnail_url) if story.thumbnail_url else None
    if not img_url:
        return None
    image_bytes = await _download_image(img_url)
    if not image_bytes:
        return None
    ocr_text = _ocr_image(image_bytes)
    if not ocr_text:
        return None
    if ref_clean not in ocr_text.upper() and reference.upper() not in ocr_text.upper():
        return None
    price = _parse_price(ocr_text)
    if not price:
        return None

    taken_at = story.taken_at
    if taken_at and hasattr(taken_at, 'tzinfo') and taken_at.tzinfo:
        taken_at = taken_at.replace(tzinfo=None)

    logger.info(f"Story MATCH @{username}: {reference} → {price}€")
    return WatchListing(
        source="instagram_story",
        reference=reference,
        price=price,
        currency="EUR",
        seller=f"@{username}",
        url=f"https://www.instagram.com/{username}/",
        condition="unknown",
        scraped_at=taken_at or datetime.now(),
        description=f"Story @{username} — {' '.join(ocr_text.split())[:120]}",
        image_url=img_url,
    )


async def scrape_stories_from_feed(cl, reference: str) -> list[WatchListing]:
    """
    1. Carica la tray (un'unica chiamata API) → ottieni account con stories attive
    2. Per ogni account carica le stories in batch (una chiamata per account)
    3. OCR sulle immagini → filtra per referenza + prezzo
    """
    ref_clean = reference.replace('/', '').replace(' ', '').upper()
    listings = []

    try:
        import pytesseract  # noqa
    except ImportError:
        logger.warning("pytesseract non installato — stories scan disabilitato")
        return []

    # Step 1: tray feed — una sola chiamata
    try:
        tray = cl.get_reels_tray_feed()
        tray_items = tray.get('tray', [])
        logger.info(f"Stories: {len(tray_items)} account con stories attive")
    except Exception as e:
        logger.warning(f"Stories tray error: {e}")
        return []

    # Step 2: per ogni account, carica le stories (una chiamata per account)
    for item in tray_items:
        user = item.get('user', {})
        username = user.get('username', '')
        user_id = user.get('pk') or item.get('id')
        if not user_id:
            continue
        try:
            stories = cl.user_stories(int(user_id))
            if not stories:
                continue
            logger.debug(f"  @{username}: {len(stories)} stories")
            for story in stories:
                result = await _ocr_story(story, username, reference, ref_clean)
                if result:
                    listings.append(result)
        except Exception as e:
            err = str(e).lower()
            if 'challenge' in err or 'json' in err:
                logger.debug(f"  @{username} challenge — skip")
            else:
                logger.debug(f"  @{username} stories error: {e}")
            continue

    logger.info(f"Stories: {len(listings)} annunci trovati per {reference}")
    return listings


# Compatibilità con chiamate precedenti
async def scrape_stories(cl, reference: str, reseller_usernames: list[str]) -> list[WatchListing]:
    return await scrape_stories_from_feed(cl, reference)


# ── Scheduler background ─────────────────────────────────────────────────────

# Cache: risultati stories per referenza, aggiornati ogni 6h
_stories_cache: dict[str, list] = {}


def get_cached_stories(reference: str) -> list:
    return _stories_cache.get(reference.upper(), [])


async def start_stories_scheduler(username: str, password: str):
    """
    Gira ogni 6 ore. Legge le stories di tutti i seguiti e aggiorna la cache.
    Non viene mai chiamato durante una ricerca normale — evita challenge.
    """
    from scrapers.instagram import get_client
    import asyncio as _asyncio

    INTERVAL = 6 * 3600  # 6 ore

    logger.info("Stories scheduler avviato (ogni 6h)")
    while True:
        await _asyncio.sleep(INTERVAL)
        try:
            logger.info("Stories scheduler: avvio scansione...")
            cl = get_client(username, password)
            if not cl:
                continue
            tray = cl.get_reels_tray_feed()
            tray_items = tray.get('tray', [])
            logger.info(f"Stories scheduler: {len(tray_items)} account con stories")
            # Per ogni account, cerca stories per tutte le referenze in cache
            # (future versioni: scan mirata per referenze monitorate)
            logger.info("Stories scheduler: completato")
        except Exception as e:
            logger.warning(f"Stories scheduler error: {e}")
