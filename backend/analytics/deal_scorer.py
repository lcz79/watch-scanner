"""Calcola deal score (0-100) per ogni listing."""
from datetime import datetime, timezone
from models.schemas import WatchListing

FULLSET_KEYWORDS = ["full set", "scatola", "garanzia", "papers", "box", "completo", "carte"]
TRUSTED_SOURCES = {"chrono24": 0.9, "ebay": 0.6, "subito": 0.4, "instagram": 0.3}


def score_listing(listing: WatchListing, market_stats: dict) -> dict:
    """
    Ritorna listing dict + campi aggiuntivi:
    {
        "deal_score": 0-100,
        "price_advantage": float,  # (market - price) / market
        "is_best_deal": bool,       # price < p25 OR price < fair_price * 0.90
        "discount_pct": float,      # % sconto vs fair_price
        "completeness_score": 0-1,
    }
    """
    fair_price = market_stats.get("fair_price")
    p25 = market_stats.get("p25")

    # Gestione edge case: dati di mercato assenti
    if fair_price is None or fair_price == 0:
        base = listing.model_dump() if hasattr(listing, "model_dump") else listing.dict()
        base.update({
            "deal_score": 50,
            "price_advantage": 0.0,
            "is_best_deal": False,
            "discount_pct": 0.0,
            "completeness_score": 0.0,
        })
        return base

    price = listing.price

    # --- Price advantage (range -1 to +1, clipped) ---
    price_advantage = (fair_price - price) / fair_price
    price_advantage = max(-1.0, min(1.0, price_advantage))

    # --- Discount pct vs fair_price ---
    discount_pct = price_advantage  # positivo = sconto, negativo = sovrapprezzo

    # --- Is best deal ---
    is_best_deal = bool(
        (p25 is not None and price < p25)
        or price < fair_price * 0.90
    )

    # --- Score components (0-100) ---

    # 1. Price score: 0-40 punti basato sul vantaggio prezzo
    #    price_advantage +1 → 40 punti, 0 → 20, -1 → 0
    price_score = (price_advantage + 1) / 2 * 40

    # 2. Dealer score: 0-25 punti basato sulla fonte
    source_lower = listing.source.lower()
    dealer_multiplier = 0.5  # default
    for key, val in TRUSTED_SOURCES.items():
        if key in source_lower:
            dealer_multiplier = val
            break
    dealer_score = dealer_multiplier * 25

    # 3. Completeness score: 0-20 punti (box & papers)
    description = (listing.description or "").lower()
    matched_keywords = sum(1 for kw in FULLSET_KEYWORDS if kw in description)
    completeness_score_raw = min(1.0, matched_keywords / 2)  # 2 keyword = completo
    completeness_score_points = completeness_score_raw * 20

    # 4. Recency score: 0-15 punti — scraped_at negli ultimi 7 giorni
    recency_score = 0.0
    try:
        now = datetime.now(timezone.utc)
        scraped = listing.scraped_at
        if scraped.tzinfo is None:
            scraped = scraped.replace(tzinfo=timezone.utc)
        age_days = (now - scraped).total_seconds() / 86400
        if age_days <= 1:
            recency_score = 15.0
        elif age_days <= 7:
            recency_score = 15.0 * (1 - (age_days - 1) / 6)
        else:
            recency_score = 0.0
    except Exception:
        recency_score = 0.0

    # Somma totale (max 100)
    deal_score = price_score + dealer_score + completeness_score_points + recency_score
    deal_score = max(0.0, min(100.0, deal_score))

    base = listing.model_dump() if hasattr(listing, "model_dump") else listing.dict()
    # Converti datetime in stringa per serializzazione JSON
    for k, v in base.items():
        if isinstance(v, datetime):
            base[k] = v.isoformat()

    base.update({
        "deal_score": round(deal_score, 2),
        "price_advantage": round(price_advantage, 4),
        "is_best_deal": is_best_deal,
        "discount_pct": round(discount_pct, 4),
        "completeness_score": round(completeness_score_raw, 2),
    })
    return base


def score_all_listings(listings: list[WatchListing], market_stats: dict) -> list[dict]:
    """Applica score_listing a tutti, ritorna lista ordinata per deal_score DESC."""
    scored = [score_listing(l, market_stats) for l in listings]
    return sorted(scored, key=lambda x: x["deal_score"], reverse=True)
