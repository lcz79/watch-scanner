"""
Pipeline principale Instagram Stories.
Coordina capture → OCR → storage per tutti i dealer prioritari.
Scheduler: ogni 2-3 ore in background.
"""
import asyncio
import random
from datetime import datetime
from utils.logger import get_logger
from models.schemas import WatchListing
from scrapers.stories.capture import (
    PRIORITY_DEALERS, capture_stories, capture_recent_posts, has_valid_auth,
)
from scrapers.stories.ocr import parse_frame
from scrapers.stories.storage import save_listing, get_stories_for_reference

logger = get_logger("stories.pipeline")

# Quanti account per run (evita ban)
MAX_ACCOUNTS_PER_RUN = 8
# Delay tra un account e l'altro (secondi)
INTER_ACCOUNT_DELAY = (8, 18)


async def process_account(username: str) -> list[dict]:
    """
    Processa un singolo account:
    1. Tenta stories → se vuoto, fallback su post recenti
    2. OCR + parsing di ogni frame
    3. Salva nel DB
    Ritorna lista di listing strutturati.
    """
    results = []

    # Tenta stories
    frames = await capture_stories(username, max_frames=15)

    # Fallback: post recenti
    if not frames:
        logger.debug(f"@{username}: nessuna story — fallback post recenti")
        frames = await capture_recent_posts(username, max_posts=6)

    if not frames:
        logger.debug(f"@{username}: nessun contenuto trovato")
        return []

    for frame in frames:
        parsed = parse_frame(
            screenshot_path=frame["screenshot_path"],
            raw_page_text=frame.get("raw_page_text", ""),
            username=frame["username"],
            timestamp=frame["timestamp"],
            post_url=frame.get("post_url", ""),
        )

        if not parsed:
            continue

        # Soglia confidenza minima
        if parsed["confidence"] < 0.4:
            logger.debug(f"@{username} frame {frame['frame_index']}: confidenza bassa ({parsed['confidence']:.2f}) — skip")
            continue

        saved = save_listing(parsed)
        if saved:
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

    target_accounts = accounts or PRIORITY_DEALERS
    # Shuffle per non colpire sempre gli stessi account per primi
    target_accounts = list(target_accounts)
    random.shuffle(target_accounts)
    target_accounts = target_accounts[:max_accounts]

    all_results = []
    logger.info(f"Stories pipeline: {len(target_accounts)} account da processare")

    for username in target_accounts:
        try:
            results = await process_account(username)
            all_results.extend(results)
        except Exception as e:
            logger.debug(f"@{username} pipeline error: {e}")

        # Delay umano tra account
        delay = random.uniform(*INTER_ACCOUNT_DELAY)
        logger.debug(f"Pausa {delay:.1f}s prima del prossimo account...")
        await asyncio.sleep(delay)

    logger.info(f"Stories pipeline completata: {len(all_results)} listing totali")
    return all_results


def stories_to_watch_listings(stories: list[dict], reference: str) -> list[WatchListing]:
    """Converte i record story in WatchListing per l'orchestratore principale."""
    listings = []
    ref_clean = reference.replace(" ", "").upper()

    for s in stories:
        # Filtra per referenza se specificata
        story_ref = (s.get("reference") or "").replace(" ", "").upper()
        story_text = (s.get("text_raw") or "").upper()
        if ref_clean and ref_clean not in story_ref and ref_clean not in story_text:
            continue

        try:
            ts = datetime.fromisoformat(s["captured_at"].replace("Z", "+00:00"))
            ts = ts.replace(tzinfo=None)
        except Exception:
            ts = datetime.now()

        listings.append(WatchListing(
            source="instagram_story",
            reference=reference,
            price=s["price"],
            currency=s.get("currency", "EUR"),
            seller=f"@{s['username']}",
            url=f"https://www.instagram.com/{s['username']}/",
            condition=s.get("condition", "unknown"),
            scraped_at=ts,
            description=s.get("text_raw", "")[:200],
            image_url=None,
        ))

    return listings


async def get_stories_listings(reference: str) -> list[WatchListing]:
    """
    Entry point per l'agente: recupera dal DB le stories recenti per una referenza.
    Non lancia la pipeline — quella gira in background ogni 2h.
    """
    stories = get_stories_for_reference(reference, hours=48)
    return stories_to_watch_listings(stories, reference)


# ── Scheduler background ──────────────────────────────────────────────────────

async def start_stories_scheduler_playwright(interval_hours: float = 2.5):
    """
    Background scheduler: gira ogni 2-3 ore.
    Chiama run_stories_pipeline() su tutti i dealer prioritari.
    """
    logger.info(f"Stories scheduler (Playwright) avviato — ogni {interval_hours}h")
    while True:
        await asyncio.sleep(interval_hours * 3600)
        try:
            logger.info("Stories scheduler: avvio run...")
            results = await run_stories_pipeline()
            logger.info(f"Stories scheduler: {len(results)} nuovi listing")
        except Exception as e:
            logger.warning(f"Stories scheduler error: {e}")
