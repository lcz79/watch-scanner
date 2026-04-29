"""
Dealer Scorer.

Calcola uno score 0-10 per ogni dealer nel DB basandosi su:
  - Classificazione confermata (is_dealer)
  - Confidence del classificatore
  - Presenza di un sito web valido
  - Numero di follower
  - Rilevamento CMS/ecommerce sul sito

Può essere eseguito stand-alone o importato dalla pipeline.
"""

import asyncio
import re
from utils.logger import get_logger
from agents.discovery import resellers_db as db

logger = get_logger("dealer_scorer")

_URL_RE = re.compile(r'^https?://.+\..+', re.I)


def _has_valid_website(dealer: dict) -> bool:
    website = dealer.get("website") or ""
    return bool(_URL_RE.match(website.strip()))


def compute_score(dealer: dict) -> float:
    """
    Calcola il score di un dealer su scala 0-10.

    Regole:
      +2  se is_dealer è True (classificato come dealer confermato)
      +0-2 da confidence (confidence * 2, massimo 2 punti)
      +2  se ha un website valido (URL http/https)
      +1  se ha followers_count > 1.000
      +1  se ha followers_count > 10.000
      +2  se ha cms_type valorizzato (sito ecommerce rilevato)

    Ritorna un float tra 0.0 e 10.0.
    """
    score = 0.0

    # +2 se dealer confermato
    if dealer.get("is_dealer") is True:
        score += 2.0

    # +0-2 da confidence
    confidence = dealer.get("confidence") or 0.0
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    score += max(0.0, min(1.0, confidence)) * 2.0

    # +2 se ha website valido
    if _has_valid_website(dealer):
        score += 2.0

    # +1 / +1 da follower
    try:
        followers = int(dealer.get("followers_count") or 0)
    except (TypeError, ValueError):
        followers = 0

    if followers > 1_000:
        score += 1.0
    if followers > 10_000:
        score += 1.0

    # +2 se CMS/ecommerce rilevato
    if dealer.get("cms_type"):
        score += 2.0

    return min(10.0, score)


async def update_all_scores():
    """
    Ricalcola e persiste il score per tutti i dealer nel DB.
    """
    conn = db._connect()
    rows = conn.execute("SELECT * FROM dealers").fetchall()
    conn.close()

    dealers = [dict(r) for r in rows]
    updated = 0

    for dealer in dealers:
        new_score = compute_score(dealer)
        if abs(new_score - (dealer.get("score") or 0.0)) > 0.001:
            db.upsert_dealer({"username": dealer["username"], "score": new_score})
            updated += 1

    logger.info(f"update_all_scores: {updated}/{len(dealers)} dealer aggiornati")
    return updated


if __name__ == "__main__":
    asyncio.run(update_all_scores())
