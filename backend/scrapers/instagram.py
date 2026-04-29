"""
Scraper Instagram per reseller di orologi.

Strategia:
1. Cerca per hashtag della referenza (#116610ln, #rolexsubmariner, #watchforsale, ecc.)
2. Monitora account reseller noti (lista aggiornabile)
3. Estrae prezzo dalla caption con regex
4. Il Vision Agent gestisce i post senza prezzo in caption

Richiede nel .env:
  INSTAGRAM_USERNAME=tuo_username
  INSTAGRAM_PASSWORD=tua_password

Il session file viene salvato in backend/instagram_session.json
per evitare login ripetuti (valido ~90 giorni).
"""

import re
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from models.schemas import WatchListing
from utils.logger import get_logger

logger = get_logger("scraper.instagram")

SESSION_FILE = Path(__file__).parent.parent / "instagram_session.json"

# Hashtag da cercare per ogni referenza
HASHTAGS_GENERIC = [
    "watchforsale",
    "orologiousato",
    "orologiusati",
    "watchreseller",
    "preloved_watches",
    "luxurywatchforsale",
]

# Account reseller di seed (fallback se il DB non è ancora stato generato)
_SEED_RESELLERS = [
    "watchesofitalia",
    "luxurywatchesmilan",
    "watchmarket_it",
    "orologi_secondmano",
    "watchhunter_eu",
    "watchdealer_milano",
]

def _get_reseller_list() -> list[str]:
    """Carica reseller dal DB discovery se disponibile, altrimenti usa il seed."""
    try:
        from agents.discovery.resellers_db import get_all_resellers
        db_list = [r["username"] for r in get_all_resellers(min_score=3, platform="instagram")]
        if db_list:
            return db_list
    except Exception:
        pass
    return _SEED_RESELLERS

# Regex per estrarre prezzo dalla caption Instagram
PRICE_PATTERNS = [
    r'(?:prezzo|price|vendesi|vendo|asking)\s*[:\-]?\s*[€$]?\s*([\d\.,]+)\s*[€$]?',
    r'[€$]\s*([\d\.,]+)',
    r'([\d\.]+[,\d]*)\s*[€$]',
    r'([\d\.]+)\s*euro',
    r'([\d\.]+)\s*eur\b',
]


def _extract_price_from_caption(caption: str) -> float | None:
    """Estrae il primo prezzo plausibile dalla caption di un post."""
    if not caption:
        return None
    caption_lower = caption.lower()
    for pattern in PRICE_PATTERNS:
        match = re.search(pattern, caption_lower)
        if match:
            raw = match.group(1).replace('.', '').replace(',', '.')
            try:
                price = float(raw)
                if 500 < price < 500_000:  # range plausibile per orologi
                    return price
            except ValueError:
                continue
    return None


def _hashtags_for_reference(reference: str) -> list[str]:
    """Genera hashtag da cercare per una referenza."""
    ref_clean = reference.replace('/', '').replace(' ', '').lower()
    brand_tags = []
    ref_upper = reference.upper()
    # Rileva brand dai prefissi comuni
    if any(ref_upper.startswith(p) for p in ['116', '126', '228', '124']):
        brand_tags = ['rolex', 'rolexforsale', 'rolexsubmariner', 'rolexdaytona']
    elif ref_upper.startswith('57') or ref_upper.startswith('51'):
        brand_tags = ['patekphilippe', 'patekforsale', 'patekphilippeforsale']
    elif ref_upper.startswith('15') or ref_upper.startswith('26'):
        brand_tags = ['audemarspiguet', 'royaloak', 'apforsale']

    return [ref_clean] + brand_tags + HASHTAGS_GENERIC


def get_client(username: str, password: str):
    """Restituisce un client instagrapi già loggato (con session cache)."""
    from instagrapi import Client
    from instagrapi.exceptions import BadPassword, TwoFactorRequired

    cl = Client()
    cl.delay_range = [2, 5]

    if SESSION_FILE.exists():
        try:
            cl.load_settings(str(SESSION_FILE))
            cl.login(username, password)
            logger.info("Instagram: login via session cache")
            return cl
        except Exception:
            logger.info("Instagram: session scaduta, rilogin...")
            SESSION_FILE.unlink(missing_ok=True)

    try:
        cl.login(username, password)
        cl.dump_settings(str(SESSION_FILE))
        logger.info("Instagram: login OK, session salvata")
        return cl
    except BadPassword:
        logger.error("Instagram: password errata")
    except TwoFactorRequired:
        logger.error("Instagram: 2FA attivo")
    except Exception as e:
        logger.error(f"Instagram login error: {e}")
    return None


async def scrape(reference: str, username: str, password: str) -> list[WatchListing]:
    """
    Scrapa Instagram per annunci della referenza specificata.
    Cerca su hashtag + monitora account reseller noti.
    """
    try:
        from instagrapi import Client  # noqa
    except ImportError:
        logger.error("instagrapi non installato. Esegui: pip install instagrapi")
        return []

    cl = get_client(username, password)
    if not cl:
        return []

    listings = []
    hashtags = _hashtags_for_reference(reference)
    session_dead = False

    # 1. Cerca per hashtag (solo i primi 2 durante la scan per velocità)
    for hashtag in hashtags[:2]:
        try:
            logger.info(f"Instagram: cercando #{hashtag}")
            medias = cl.hashtag_medias_recent_v1(hashtag, amount=15)
            for media in medias:
                listing = _media_to_listing(media, reference, cl)
                if listing:
                    listings.append(listing)
            await asyncio.sleep(1)
        except Exception as e:
            err_str = str(e).lower()
            logger.warning(f"Hashtag #{hashtag} error: {e}")
            if "login_required" in err_str or "challenge_required" in err_str:
                session_dead = True
                break  # Session morta — inutile continuare
            continue

    # 2. Monitora account reseller solo se la sessione è viva
    if session_dead:
        logger.warning("Instagram: sessione scaduta, skip account monitoring")
        SESSION_FILE.unlink(missing_ok=True)  # Forza re-login al prossimo avvio
    else:
        resellers = _get_reseller_list()
        logger.info(f"Monitorando {min(5, len(resellers))} account reseller")
        consecutive_errors = 0
        for account in resellers[:5]:
            try:
                loop = asyncio.get_event_loop()
                user_id = await loop.run_in_executor(None, cl.user_id_from_username, account)
                medias = await loop.run_in_executor(None, lambda: cl.user_medias(user_id, amount=12))
                for media in medias:
                    listing = _media_to_listing(media, reference, cl)
                    if listing:
                        listings.append(listing)
                consecutive_errors = 0
                await asyncio.sleep(2)
            except Exception as e:
                err_str = str(e).lower()
                logger.debug(f"Account @{account} error: {e}")
                if "login_required" in err_str or "challenge_required" in err_str:
                    consecutive_errors += 1
                    if consecutive_errors >= 2:
                        logger.warning("Instagram: troppi login_required, stop account monitoring")
                        SESSION_FILE.unlink(missing_ok=True)
                        break
                continue

    # Deduplicazione per URL
    seen = set()
    unique = []
    for l in listings:
        if l.url not in seen:
            seen.add(l.url)
            unique.append(l)

    logger.info(f"Instagram: {len(unique)} annunci trovati per {reference}")
    return unique


def _media_to_listing(media, reference: str, cl) -> WatchListing | None:
    """Converte un media Instagram in un WatchListing se rilevante."""
    try:
        caption = media.caption_text or ""
        ref_clean = reference.replace('/', '').replace(' ', '').upper()

        # La referenza deve essere presente in caption (sia per hashtag che per reseller)
        if ref_clean not in caption.upper() and reference.upper() not in caption.upper():
            return None

        price = _extract_price_from_caption(caption)
        if not price:
            return None

        # URL del post
        code = media.code
        post_url = f"https://www.instagram.com/p/{code}/"

        # Username del venditore
        username = media.user.username if hasattr(media, 'user') and media.user else "instagram_user"

        # Immagine
        image_url = None
        if hasattr(media, 'thumbnail_url') and media.thumbnail_url:
            image_url = str(media.thumbnail_url)

        # Timestamp
        taken_at = media.taken_at if hasattr(media, 'taken_at') else datetime.now(timezone.utc)
        if taken_at and taken_at.tzinfo:
            taken_at = taken_at.replace(tzinfo=None)

        return WatchListing(
            source="instagram",
            reference=reference,
            price=price,
            currency="EUR",
            seller=f"@{username}",
            url=post_url,
            condition="unknown",
            scraped_at=taken_at or datetime.now(),
            image_url=image_url,
            description=caption[:200],
        )
    except Exception as e:
        logger.debug(f"Media parse error: {e}")
        return None
