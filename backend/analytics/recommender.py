"""Recommendation engine — trova i migliori orologi da comprare ora."""
import time
from datetime import datetime, timezone

from analytics.market_engine import compute_market_stats
from analytics.deal_scorer import score_all_listings
from analytics.investment_scorer import compute_investment_score

# Cache in-memory {reference: {stats, scored_listings, investment, timestamp}}
_cache: dict = {}
CACHE_TTL_SECONDS = 600  # 10 minuti


def _is_cache_fresh(entry: dict) -> bool:
    return (time.time() - entry.get("timestamp", 0)) < CACHE_TTL_SECONDS


async def analyze_reference(reference: str, listings: list) -> dict:
    """
    Analizza una referenza, usa cache se fresca.
    Ritorna: {reference, market_stats, best_listings (top 5), investment, top_deal}
    """
    if reference in _cache and _is_cache_fresh(_cache[reference]):
        return _cache[reference]["result"]

    from models.schemas import WatchListing

    # Converti in WatchListing se sono dict
    watch_listings: list[WatchListing] = []
    for item in listings:
        if isinstance(item, WatchListing):
            watch_listings.append(item)
        elif isinstance(item, dict):
            try:
                watch_listings.append(WatchListing(**item))
            except Exception:
                pass

    market_stats = compute_market_stats(watch_listings)
    scored = score_all_listings(watch_listings, market_stats)
    investment = compute_investment_score(reference, market_stats, len(watch_listings))

    best_listings = scored[:5]
    top_deal = scored[0] if scored else None

    result = {
        "reference": reference,
        "market_stats": market_stats,
        "best_listings": best_listings,
        "investment": investment,
        "top_deal": top_deal,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }

    _cache[reference] = {
        "result": result,
        "timestamp": time.time(),
    }

    return result


async def get_recommendations(all_scan_results: list[dict]) -> list[dict]:
    """
    Input: lista di {reference, listings}
    Calcola global_score = deal_score * 0.5 + investment_score * 0.3 + liquidity * 0.2
    Ritorna top 3 referenze ordinate per global_score.
    """
    LIQUIDITY_MAP = {"high": 100.0, "medium": 60.0, "low": 20.0}

    scored_refs = []
    for item in all_scan_results:
        reference = item.get("reference", "")
        listings = item.get("listings", [])

        if not reference or not listings:
            continue

        analysis = await analyze_reference(reference, listings)

        market_stats = analysis["market_stats"]
        investment = analysis["investment"]
        top_deal = analysis["top_deal"]

        deal_score = top_deal["deal_score"] if top_deal else 0.0
        investment_score = investment.get("investment_score", 0.0)
        liquidity_score = LIQUIDITY_MAP.get(investment.get("liquidity", "low"), 20.0)

        global_score = (
            deal_score * 0.5
            + investment_score * 0.3
            + liquidity_score * 0.2
        )

        scored_refs.append({
            "reference": reference,
            "global_score": round(global_score, 2),
            "deal_score": deal_score,
            "investment_score": investment_score,
            "liquidity": investment.get("liquidity"),
            "signal": investment.get("signal"),
            "top_deal": top_deal,
            "market_stats": market_stats,
        })

    scored_refs.sort(key=lambda x: x["global_score"], reverse=True)
    return scored_refs[:3]
