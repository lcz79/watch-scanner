"""
Scheduler settimanale per lo scraping delle aste.
Prima run: 2 minuti dopo l'avvio.
Poi: ogni 7 giorni.
"""
import asyncio
from datetime import datetime

from utils.logger import get_logger
from .database import bulk_insert_results, count_results

logger = get_logger("auctions")

# Stato ultimo refresh — accessibile dall'endpoint
_refresh_status: dict = {
    "last_run": None,
    "last_run_status": "never",
    "last_run_sources": {},
    "next_run": None,
    "is_running": False,
}

_INITIAL_DELAY_SECONDS = 120   # 2 minuti
_INTERVAL_SECONDS = 7 * 24 * 3600  # 7 giorni


def get_refresh_status() -> dict:
    """Ritorna lo stato dell'ultimo refresh."""
    return dict(_refresh_status)


async def run_full_refresh() -> dict:
    """
    Esegue lo scraping completo di tutte le fonti aste.
    Ritorna un dict con statistiche del run.
    """
    if _refresh_status["is_running"]:
        logger.info("Auction scheduler: refresh già in corso, skip")
        return {"status": "already_running"}

    _refresh_status["is_running"] = True
    _refresh_status["last_run"] = datetime.utcnow().isoformat()
    stats: dict = {}

    logger.info("Auction scheduler: avvio refresh completo aste")

    # ── 1. Invaluable: ricerca lotti per referenze chiave ──────────────────
    try:
        from .scrapers.invaluable_scraper import search_reference

        KEY_REFERENCES = [
            "Rolex Daytona", "Patek Philippe Nautilus", "Rolex Submariner",
            "Audemars Piguet Royal Oak", "F.P. Journe",
        ]
        invaluable_results = []
        for ref in KEY_REFERENCES:
            try:
                lots = await search_reference(ref, limit=20)
                invaluable_results.extend(lots)
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Invaluable search '{ref}' error: {e}")

        inserted_inv = bulk_insert_results(invaluable_results)
        stats["invaluable"] = {"found": len(invaluable_results), "inserted": inserted_inv}
        logger.info(f"Invaluable: {len(invaluable_results)} trovati, {inserted_inv} inseriti")

    except Exception as e:
        logger.error(f"Invaluable scraper error: {e}")
        stats["invaluable"] = {"error": str(e)}

    await asyncio.sleep(2)

    # ── 2. Phillips: risultati recenti ────────────────────────────────────
    try:
        from .scrapers.phillips_scraper import scrape_recent_results as phillips_scrape

        phillips_results = await phillips_scrape(limit=50)
        inserted_phi = bulk_insert_results(phillips_results)
        stats["phillips"] = {"found": len(phillips_results), "inserted": inserted_phi}
        logger.info(f"Phillips: {len(phillips_results)} trovati, {inserted_phi} inseriti")

    except Exception as e:
        logger.error(f"Phillips scraper error: {e}")
        stats["phillips"] = {"error": str(e)}

    await asyncio.sleep(3)

    # ── 3. Christie's: risultati recenti ─────────────────────────────────
    try:
        from .scrapers.christies_scraper import scrape_recent_results as christies_scrape

        christies_results = await christies_scrape(limit=50)
        inserted_chr = bulk_insert_results(christies_results)
        stats["christies"] = {"found": len(christies_results), "inserted": inserted_chr}
        logger.info(f"Christie's: {len(christies_results)} trovati, {inserted_chr} inseriti")

    except Exception as e:
        logger.error(f"Christie's scraper error: {e}")
        stats["christies"] = {"error": str(e)}

    await asyncio.sleep(3)

    # ── 4. Sotheby's: risultati recenti ───────────────────────────────────
    try:
        from .scrapers.sotherby_scraper import scrape_recent_results as sothebys_scrape

        sothebys_results = await sothebys_scrape(limit=50)
        inserted_sot = bulk_insert_results(sothebys_results)
        stats["sothebys"] = {"found": len(sothebys_results), "inserted": inserted_sot}
        logger.info(f"Sotheby's: {len(sothebys_results)} trovati, {inserted_sot} inseriti")

    except Exception as e:
        logger.error(f"Sotheby's scraper error: {e}")
        stats["sothebys"] = {"error": str(e)}

    await asyncio.sleep(3)

    # ── 5. Antiquorum: risultati recenti ──────────────────────────────────
    try:
        from .scrapers.antiquorum_scraper import scrape_recent_results as antiquorum_scrape

        antiquorum_results = await antiquorum_scrape(limit=40)
        inserted_ant = bulk_insert_results(antiquorum_results)
        stats["antiquorum"] = {"found": len(antiquorum_results), "inserted": inserted_ant}
        logger.info(f"Antiquorum: {len(antiquorum_results)} trovati, {inserted_ant} inseriti")

    except Exception as e:
        logger.error(f"Antiquorum scraper error: {e}")
        stats["antiquorum"] = {"error": str(e)}

    await asyncio.sleep(3)

    # ── 7. Upcoming auctions live ────────────────────────────────────────
    try:
        from .scrapers.upcoming_scraper import scrape_all_upcoming

        upcoming = await scrape_all_upcoming()
        stats["upcoming"] = {"found": len(upcoming)}

        # Aggiorna il calendario live nel modulo calendar (cache in memoria)
        if upcoming:
            from . import calendar as _calendar
            _calendar._LIVE_UPCOMING_CACHE = upcoming
            logger.info(f"Upcoming cache aggiornata: {len(upcoming)} aste")

    except Exception as e:
        logger.error(f"Upcoming scraper error: {e}")
        stats["upcoming"] = {"error": str(e)}

    # ── 4. Aggiorna stato ────────────────────────────────────────────────
    _refresh_status["is_running"] = False
    _refresh_status["last_run_status"] = "success"
    _refresh_status["last_run_sources"] = stats
    _refresh_status["total_in_db"] = count_results()

    logger.info(f"Auction scheduler: refresh completato. Stats: {stats}")
    return {"status": "completed", "stats": stats}


async def start_auction_scheduler():
    """
    Scheduler asincrono per lo scraping periodico delle aste.
    Prima run dopo _INITIAL_DELAY_SECONDS, poi ogni _INTERVAL_SECONDS.
    """
    logger.info(
        f"Auction scheduler: avviato. Prima run tra {_INITIAL_DELAY_SECONDS}s, "
        f"poi ogni {_INTERVAL_SECONDS // 3600}h"
    )

    # Calcola prossima run
    from datetime import datetime, timedelta

    _refresh_status["next_run"] = (
        datetime.utcnow() + timedelta(seconds=_INITIAL_DELAY_SECONDS)
    ).isoformat()

    try:
        await asyncio.sleep(_INITIAL_DELAY_SECONDS)

        while True:
            try:
                await run_full_refresh()
            except Exception as e:
                logger.error(f"Auction scheduler: errore run: {e}")
                _refresh_status["last_run_status"] = f"error: {e}"
                _refresh_status["is_running"] = False

            _refresh_status["next_run"] = (
                datetime.utcnow() + timedelta(seconds=_INTERVAL_SECONDS)
            ).isoformat()

            logger.info(
                f"Auction scheduler: prossima run tra {_INTERVAL_SECONDS // 3600}h "
                f"({_refresh_status['next_run']})"
            )
            await asyncio.sleep(_INTERVAL_SECONDS)

    except asyncio.CancelledError:
        logger.info("Auction scheduler: cancellato")
