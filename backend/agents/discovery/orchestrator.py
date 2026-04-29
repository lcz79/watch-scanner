"""
Discovery Orchestrator.

Coordina tutti i discovery agent (Instagram, Facebook, TikTok)
e aggiorna il database dei reseller.

Può essere lanciato:
  - Da riga di comando: python -m agents.discovery.orchestrator
  - Via API: POST /discovery/start
  - Automaticamente come task periodico (ogni notte alle 3:00)

Il processo è pensato per girare in background senza bloccare il server principale.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger
from agents.discovery import resellers_db as db_module

logger = get_logger("discovery.orchestrator")

# Stato globale del discovery (per l'API)
_discovery_state = {
    "running": False,
    "started_at": None,
    "progress": {},
    "last_run": None,
    "total_found": 0,
}


def get_state() -> dict:
    return {**_discovery_state, "db_stats": db_module.get_stats()}


async def run_full_discovery(instagram_username: str = "", instagram_password: str = ""):
    """
    Lancia la discovery completa su tutte le piattaforme.
    Progresso salvato in _discovery_state per l'API.
    """
    global _discovery_state

    if _discovery_state["running"]:
        logger.warning("Discovery già in esecuzione, skip")
        return

    _discovery_state["running"] = True
    _discovery_state["started_at"] = datetime.now().isoformat()
    _discovery_state["progress"] = {
        "instagram": "pending",
        "facebook": "pending",
        "tiktok": "pending",
    }
    _discovery_state["total_found"] = 0

    db = db_module.load()
    logger.info(f"=== Discovery avviata | DB attuale: {len(db['resellers'])} reseller ===")

    try:
        # Instagram (richiede credenziali)
        if instagram_username and instagram_password:
            _discovery_state["progress"]["instagram"] = "running"
            try:
                ig_found = await _run_instagram(db, instagram_username, instagram_password)
                _discovery_state["progress"]["instagram"] = f"done ({ig_found} nuovi)"
                _discovery_state["total_found"] += ig_found
            except Exception as e:
                logger.error(f"Instagram discovery error: {e}")
                _discovery_state["progress"]["instagram"] = f"error: {e}"
        else:
            _discovery_state["progress"]["instagram"] = "skip (no credentials)"

        # Facebook + TikTok via Playwright
        _discovery_state["progress"]["facebook"] = "running"
        _discovery_state["progress"]["tiktok"] = "running"

        fb_found, tt_found = await _run_browser_agents(db)

        _discovery_state["progress"]["facebook"] = f"done ({fb_found} nuovi)"
        _discovery_state["progress"]["tiktok"] = f"done ({tt_found} nuovi)"
        _discovery_state["total_found"] += fb_found + tt_found

    finally:
        db_module.save(db)
        _discovery_state["running"] = False
        _discovery_state["last_run"] = datetime.now().isoformat()

        stats = db_module.get_stats()
        logger.info(
            f"=== Discovery completata | "
            f"Totale DB: {stats['total']} reseller | "
            f"Nuovi questa sessione: {_discovery_state['total_found']} | "
            f"IG={_discovery_state['progress']['instagram']} | "
            f"FB={_discovery_state['progress']['facebook']} | "
            f"TT={_discovery_state['progress']['tiktok']} ==="
        )


async def _run_instagram(db: dict, username: str, password: str) -> int:
    """Lancia Instagram discovery con instagrapi."""
    from instagrapi import Client
    from agents.discovery.instagram_discovery import run as ig_run

    SESSION_FILE = Path(__file__).parent.parent.parent / "instagram_session.json"
    cl = Client()
    cl.delay_range = [2, 4]

    if SESSION_FILE.exists():
        try:
            cl.load_settings(str(SESSION_FILE))
            cl.login(username, password)
        except Exception:
            SESSION_FILE.unlink(missing_ok=True)
            cl.login(username, password)
            cl.dump_settings(str(SESSION_FILE))
    else:
        cl.login(username, password)
        cl.dump_settings(str(SESSION_FILE))

    logger.info(f"Instagram: login OK come @{username}")
    return await ig_run(cl, db, max_per_hashtag=30, expand_network=True)


async def _run_browser_agents(db: dict) -> tuple[int, int]:
    """Lancia Facebook + TikTok discovery in parallelo con Playwright."""
    from playwright.async_api import async_playwright
    from agents.discovery.facebook_discovery import run as fb_run
    from agents.discovery.tiktok_discovery import run as tt_run

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="it-IT",
        )

        fb_found, tt_found = await asyncio.gather(
            fb_run(context, db),
            tt_run(context, db),
            return_exceptions=False,
        )

        await browser.close()

    return fb_found, tt_found


# ── Scheduler notturno ──────────────────────────────────────────────────────

async def start_nightly_scheduler(instagram_username: str, instagram_password: str):
    """
    Lancia la discovery automaticamente ogni notte alle 3:00.
    Da chiamare all'avvio del server FastAPI.
    """
    import time

    logger.info("Scheduler notturno discovery avviato (ogni notte alle 03:00)")
    while True:
        now = datetime.now()
        # Calcola secondi fino alle prossime 03:00
        next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run = next_run.replace(day=now.day + 1)
        wait_seconds = (next_run - now).total_seconds()
        logger.info(f"Prossima discovery alle {next_run.strftime('%H:%M')} (tra {wait_seconds/3600:.1f}h)")
        await asyncio.sleep(wait_seconds)
        await run_full_discovery(instagram_username, instagram_password)


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import argparse
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    parser = argparse.ArgumentParser(description="WatchScanner Discovery Orchestrator")
    parser.add_argument("--ig-username", default="", help="Username Instagram")
    parser.add_argument("--ig-password", default="", help="Password Instagram")
    args = parser.parse_args()

    asyncio.run(run_full_discovery(
        instagram_username=args.ig_username,
        instagram_password=args.ig_password,
    ))
