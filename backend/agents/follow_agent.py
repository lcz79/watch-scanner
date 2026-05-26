"""
Follow Agent — segue automaticamente i reseller scoperti dal discovery.

Anti-detection by design:
  - Nessun intervallo fisso: il scheduler sceglie un delay casuale ogni volta (2-9h)
  - Nessun conteggio fisso: 1-5 follow per sessione, distribuiti non uniformemente
  - Delay variabile tra un follow e l'altro: 25-180s, con distribuzione non lineare
  - Pausa "browse" prima di seguire (simula lettura del profilo)
  - Cap giornaliero morbido: max 15 follow/giorno
  - Salta giorni casuali (~20% delle sessioni notturne)

Requisiti: INSTAGRAM_USERNAME e INSTAGRAM_PASSWORD nel .env
"""

import asyncio
import random
from datetime import datetime, date, timedelta
from utils.logger import get_logger

logger = get_logger("follow_agent")

# Limiti di sicurezza
MAX_FOLLOWS_PER_DAY = 15
MIN_SCORE_TO_FOLLOW = 4.0


def _get_daily_count() -> int:
    """Conta i follow fatti oggi dal DB."""
    try:
        from agents.discovery.resellers_db import _connect
        conn = _connect()
        today = date.today().isoformat()
        count = conn.execute(
            "SELECT COUNT(*) FROM dealers WHERE followed_at >= ?", (today,)
        ).fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def _get_unfollowed_resellers(limit: int = 50) -> list[dict]:
    """Reseller con score alto non ancora seguiti."""
    try:
        from agents.discovery.resellers_db import _connect
        conn = _connect()
        rows = conn.execute(
            "SELECT username, score, followers_count FROM dealers "
            "WHERE followed_at IS NULL "
            "AND score >= ? "
            "AND platform = 'instagram' "
            "AND (is_dealer = 1 OR is_dealer IS NULL) "
            "ORDER BY score DESC, RANDOM() "
            "LIMIT ?",
            (MIN_SCORE_TO_FOLLOW, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Errore lettura reseller: {e}")
        return []


def _mark_followed(username: str):
    """Segna l'account come seguito nel DB."""
    try:
        from agents.discovery.resellers_db import _connect
        conn = _connect()
        with conn:
            conn.execute(
                "UPDATE dealers SET followed_at = ? WHERE username = ?",
                (datetime.now().isoformat(), username),
            )
        conn.close()
    except Exception as e:
        logger.error(f"Errore mark_followed @{username}: {e}")


def _random_follow_count() -> int:
    """
    Sceglie quanti account seguire in questa sessione.
    Pesi volutamente asimmetrici — non uniforme.
    """
    # 50% → 1-2, 30% → 3, 15% → 4, 5% → 5
    roll = random.random()
    if roll < 0.30:
        return 1
    elif roll < 0.55:
        return 2
    elif roll < 0.85:
        return 3
    elif roll < 0.95:
        return 4
    else:
        return 5


def _random_inter_follow_delay() -> float:
    """
    Delay in secondi tra un follow e l'altro.
    Non uniforme: mix di pause brevi e lunghe, come un umano.
    """
    # 60% chance pausa normale (25-90s), 30% pausa lunga (90-200s), 10% pausa breve (12-30s)
    roll = random.random()
    if roll < 0.10:
        return random.uniform(12, 30)
    elif roll < 0.70:
        return random.uniform(25, 90)
    else:
        return random.uniform(90, 200)


async def run_follow_session(cl) -> int:
    """
    Esegue una sessione di follow con comportamento casuale.
    Ritorna il numero di account seguiti.
    """
    daily_count = _get_daily_count()
    if daily_count >= MAX_FOLLOWS_PER_DAY:
        logger.info(f"[follow] Cap giornaliero raggiunto ({daily_count}/{MAX_FOLLOWS_PER_DAY}) — skip")
        return 0

    candidates = _get_unfollowed_resellers(limit=30)
    if not candidates:
        logger.info("[follow] Nessun nuovo reseller da seguire")
        return 0

    # Quanti ne seguiamo questa sessione (rispettando il cap)
    remaining = MAX_FOLLOWS_PER_DAY - daily_count
    n = min(_random_follow_count(), remaining, len(candidates))

    # Shuffle leggero sui candidati (non sempre i top-score)
    # 70% prende dai top-10, 30% pesca casuale da tutta la lista
    if random.random() < 0.30 and len(candidates) > 10:
        selected = random.sample(candidates, n)
    else:
        selected = random.sample(candidates[:min(10, len(candidates))], min(n, min(10, len(candidates))))

    followed = 0
    for account in selected:
        username = account["username"]
        try:
            # Pausa "browse" prima di seguire — simula lettura profilo
            browse_pause = random.uniform(4, 18)
            logger.debug(f"[follow] Visita profilo @{username} ({browse_pause:.0f}s)...")
            await asyncio.sleep(browse_pause)

            # Recupera user_id e segui
            loop = asyncio.get_event_loop()
            user_id = await loop.run_in_executor(None, cl.user_id_from_username, username)
            await loop.run_in_executor(None, cl.user_follow, user_id)

            _mark_followed(username)
            followed += 1
            logger.info(f"[follow] ✓ @{username} (score={account['score']:.1f}) — {followed}/{n} questa sessione, {daily_count + followed}/{MAX_FOLLOWS_PER_DAY} oggi")

            # Delay tra follow (solo se non è l'ultimo)
            if followed < n:
                delay = _random_inter_follow_delay()
                logger.debug(f"[follow] Attesa {delay:.0f}s prima del prossimo...")
                await asyncio.sleep(delay)

        except Exception as e:
            err = str(e).lower()
            logger.warning(f"[follow] @{username} fallito: {type(e).__name__}: {str(e)[:80]}")
            if "login_required" in err or "challenge_required" in err:
                logger.error("[follow] Sessione Instagram morta — stop")
                break
            # Su errore generico aspetta un po' prima di continuare
            await asyncio.sleep(random.uniform(15, 45))

    logger.info(f"[follow] Sessione completata: {followed} follow eseguiti")
    return followed


async def start_follow_scheduler(instagram_username: str, instagram_password: str):
    """
    Scheduler con intervalli completamente casuali.
    Nessun orario fisso, nessun pattern riconoscibile.
    """
    logger.info("[follow] Scheduler avviato — primo run tra 30-90 min")

    # Prima run: attesa casuale iniziale (non parte subito all'avvio del server)
    await asyncio.sleep(random.uniform(1800, 5400))  # 30-90 min

    while True:
        try:
            # ~20% delle volte salta completamente la sessione
            if random.random() < 0.20:
                skip_hours = random.uniform(1.5, 5)
                logger.info(f"[follow] Sessione saltata casualmente — riprendo tra {skip_hours:.1f}h")
                await asyncio.sleep(skip_hours * 3600)
                continue

            # Login
            from scrapers.instagram import get_client
            loop = asyncio.get_event_loop()
            cl = await loop.run_in_executor(None, get_client, instagram_username, instagram_password)

            if cl:
                await run_follow_session(cl)
            else:
                logger.warning("[follow] Login Instagram fallito — riprovo più tardi")

        except asyncio.CancelledError:
            logger.info("[follow] Scheduler interrotto")
            return
        except Exception as e:
            logger.error(f"[follow] Errore sessione: {e}")

        # Attesa casuale prima della prossima sessione: 2-9 ore
        # Non uniforme: più probabile 3-6h, meno probabile <2h o >8h
        base = random.uniform(2, 6)
        jitter = random.uniform(-0.5, 2.5)
        next_hours = max(2.0, base + jitter)
        logger.info(f"[follow] Prossima sessione tra {next_hours:.1f}h")
        await asyncio.sleep(next_hours * 3600)
