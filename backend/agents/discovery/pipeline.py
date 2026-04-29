"""
Discovery Pipeline.

Orchestratore del ciclo completo di discovery:
  1. Instagram discovery    — trova nuovi account reseller via hashtag/rete
  2. Classificazione        — classifica gli account non ancora analizzati
  3. Website crawl          — crawla i siti web dei dealer confermati
  4. Score update           — ricalcola gli score di tutti i dealer

Può girare una volta sola (run_discovery_once) o in loop continuo
(run_continuous). Ogni step è isolato: se un modulo non è disponibile
viene loggato e la pipeline continua con gli step successivi.
"""

import asyncio
from datetime import datetime
from utils.logger import get_logger
from agents.discovery import resellers_db as db_module

logger = get_logger("discovery.pipeline")


async def _step_instagram_discovery() -> int:
    """
    Step 1 — Instagram discovery.
    Importa instagram_discovery e lancia il crawl via hashtag + network expansion.
    Richiede instagrapi installato e credenziali configurate.
    Ritorna il numero di nuovi dealer trovati.
    """
    try:
        from agents.discovery.instagram_discovery import run as ig_run
    except ImportError as e:
        logger.warning(f"[pipeline] instagram_discovery non disponibile: {e}")
        return 0

    try:
        from config import settings  # type: ignore
        ig_user = getattr(settings, "instagram_username", "") or ""
        ig_pass = getattr(settings, "instagram_password", "") or ""
    except Exception:
        ig_user = ig_pass = ""

    if not ig_user or not ig_pass:
        logger.info("[pipeline] Instagram skip: credenziali non configurate")
        return 0

    try:
        from instagrapi import Client  # type: ignore
        from pathlib import Path

        SESSION_FILE = Path(__file__).parent.parent.parent / "instagram_session.json"
        cl = Client()
        cl.delay_range = [2, 4]

        if SESSION_FILE.exists():
            try:
                cl.load_settings(str(SESSION_FILE))
                cl.login(ig_user, ig_pass)
            except Exception:
                SESSION_FILE.unlink(missing_ok=True)
                cl.login(ig_user, ig_pass)
                cl.dump_settings(str(SESSION_FILE))
        else:
            cl.login(ig_user, ig_pass)
            cl.dump_settings(str(SESSION_FILE))

        logger.info(f"[pipeline] Instagram login OK come @{ig_user}")
        db = db_module.load()
        found = await ig_run(cl, db, max_per_hashtag=30, expand_network=True)
        db_module.save(db)
        logger.info(f"[pipeline] Instagram discovery: {found} nuovi dealer")
        return found

    except Exception as e:
        logger.error(f"[pipeline] Instagram discovery errore: {e}")
        return 0


async def _step_classify_pending() -> int:
    """
    Step 2 — Classifica account non ancora classificati.
    Importa vision_agent o un classificatore heuristic.
    Ritorna il numero di account classificati.
    """
    pending = db_module.get_pending_classification()
    if not pending:
        logger.info("[pipeline] Classificazione: nessun account in attesa")
        return 0

    logger.info(f"[pipeline] Classificazione: {len(pending)} account da classificare")

    try:
        from agents.vision_agent import classify_dealer  # type: ignore
        classifier = classify_dealer
    except ImportError:
        # Fallback: classificazione euristica basata su score soglia
        def classifier(dealer: dict):  # type: ignore[misc]
            score = dealer.get("score", 0) or 0
            if score >= 5:
                return True, min(1.0, score / 10.0)
            if score < 2:
                return False, 0.1
            return None, None  # non classificato

    classified = 0
    for dealer in pending:
        try:
            is_dealer, confidence = classifier(dealer)
            if is_dealer is not None:
                db_module.upsert_dealer({
                    "username": dealer["username"],
                    "is_dealer": is_dealer,
                    "confidence": confidence,
                })
                db_module.log_crawl(
                    dealer["username"], "classifier",
                    "classified",
                    f"is_dealer={is_dealer} confidence={confidence:.2f}",
                )
                classified += 1
        except Exception as e:
            logger.warning(f"[pipeline] Errore classificazione @{dealer['username']}: {e}")

    logger.info(f"[pipeline] Classificazione: {classified}/{len(pending)} classificati")
    return classified


async def _step_website_crawl() -> int:
    """
    Step 3 — Crawla i siti web dei dealer con website non ancora crawlato.
    Importa reseller_website_agent se disponibile.
    Ritorna il numero di siti crawlati.
    """
    pending = db_module.get_pending_website_crawl()
    if not pending:
        logger.info("[pipeline] Website crawl: nessun sito in attesa")
        return 0

    logger.info(f"[pipeline] Website crawl: {len(pending)} siti da analizzare")

    try:
        from agents.reseller_website_agent import crawl_website  # type: ignore
        crawl_fn = crawl_website
    except ImportError as e:
        logger.warning(f"[pipeline] reseller_website_agent non disponibile: {e}")
        return 0

    crawled = 0
    for dealer in pending:
        username = dealer["username"]
        website = dealer.get("website", "")
        try:
            result = await crawl_fn(website)
            db_module.upsert_dealer({
                "username": username,
                "cms_type": result.get("cms_type"),
                "last_crawled": datetime.now().isoformat(),
            })
            db_module.log_crawl(
                username, "website_crawl", "ok",
                f"cms={result.get('cms_type')} url={website}",
            )
            crawled += 1
        except Exception as e:
            logger.warning(f"[pipeline] Crawl fallito per @{username} ({website}): {e}")
            db_module.log_crawl(username, "website_crawl", "error", str(e))
            db_module.upsert_dealer({
                "username": username,
                "last_crawled": datetime.now().isoformat(),
            })

    logger.info(f"[pipeline] Website crawl: {crawled}/{len(pending)} completati")
    return crawled


async def _step_update_scores() -> int:
    """
    Step 4 — Ricalcola gli score di tutti i dealer.
    """
    try:
        from agents.discovery.dealer_scorer import update_all_scores
        updated = await update_all_scores()
        logger.info(f"[pipeline] Score aggiornati: {updated} dealer")
        return updated
    except Exception as e:
        logger.error(f"[pipeline] Errore aggiornamento score: {e}")
        return 0


async def run_discovery_once():
    """
    Esegue un ciclo completo di discovery.

    Step eseguiti in sequenza:
      1. Instagram discovery
      2. Classificazione account non classificati
      3. Crawl siti web dealer confermati
      4. Aggiornamento score
    """
    started = datetime.now()
    logger.info(f"=== Discovery avviata: {started.strftime('%Y-%m-%d %H:%M:%S')} ===")

    results = {}

    results["instagram"] = await _step_instagram_discovery()
    results["classified"] = await _step_classify_pending()
    results["website_crawl"] = await _step_website_crawl()
    results["scores_updated"] = await _step_update_scores()

    elapsed = (datetime.now() - started).total_seconds()
    logger.info(
        f"=== Discovery completata in {elapsed:.1f}s | "
        f"IG={results['instagram']} nuovi | "
        f"classificati={results['classified']} | "
        f"crawled={results['website_crawl']} | "
        f"score_updated={results['scores_updated']} ==="
    )
    return results


async def run_continuous(interval_hours: float = 6):
    """
    Loop continuo di discovery.
    Esegue run_discovery_once() ogni interval_hours ore.
    """
    logger.info(f"[pipeline] Loop continuo avviato (ogni {interval_hours}h)")
    while True:
        try:
            await run_discovery_once()
        except Exception as e:
            logger.error(f"[pipeline] Errore nel ciclo discovery: {e}")
        logger.info(f"[pipeline] Prossimo ciclo tra {interval_hours}h")
        await asyncio.sleep(interval_hours * 3600)


if __name__ == "__main__":
    asyncio.run(run_discovery_once())
