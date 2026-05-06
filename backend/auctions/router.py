"""
FastAPI router per il sistema aste mondiali.
Prefisso: /auctions
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from utils.logger import get_logger
from .database import (
    get_results_by_reference,
    get_records,
    get_all_auction_houses,
    get_recent_results,
    bulk_insert_results,
    upsert_sentiment,
    get_sentiment,
    count_results,
)
from .sentiment import compute_sentiment, enrich_results
from .calendar import get_upcoming_auctions, get_auction_houses_info

logger = get_logger("auctions")

router = APIRouter(prefix="/auctions", tags=["auctions"])


# ---------------------------------------------------------------------------
# Risultati aste per referenza
# ---------------------------------------------------------------------------

@router.get("/results/{reference}")
async def get_auction_results(
    reference: str,
    limit: int = Query(default=20, ge=1, le=200),
    sort_by: str = Query(default="date", regex="^(date|price|performance)$"),
) -> dict:
    """
    Tutti i risultati d'asta storici per una referenza.
    sort_by: 'date' | 'price' | 'performance'
    """
    reference = reference.strip()
    if not reference:
        raise HTTPException(status_code=400, detail="Reference non può essere vuota")

    results = get_results_by_reference(reference, limit=limit, sort_by=sort_by)
    enriched = enrich_results(results)

    return {
        "reference": reference,
        "total": len(enriched),
        "sort_by": sort_by,
        "results": enriched,
    }


# ---------------------------------------------------------------------------
# Sentiment score per referenza
# ---------------------------------------------------------------------------

@router.get("/sentiment/{reference}")
async def get_auction_sentiment(reference: str) -> dict:
    """
    Sentiment score basato sui risultati d'asta storici.
    Score 0-100: Strong Buy / Accumulate / Hold / Reduce / Sell.
    """
    reference = reference.strip()
    if not reference:
        raise HTTPException(status_code=400, detail="Reference non può essere vuota")

    # Cerca in cache DB
    cached = get_sentiment(reference)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if cached and cached.get("calculation_date") == today:
        logger.debug(f"Sentiment {reference}: cache hit")
        return cached

    # Calcola live
    results = get_results_by_reference(reference, limit=200)
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Nessun dato d'asta per referenza '{reference}'. Seed il DB prima.",
        )

    # Determina brand
    brand = results[0].get("brand", "Unknown") if results else "Unknown"

    sentiment = compute_sentiment(reference, results)

    # Persisti
    sentiment_db = {
        "reference": reference,
        "brand": brand,
        "calculation_date": today,
        "total_lots": sentiment["total_auction_records"],
        "avg_hammer_to_estimate_ratio": sentiment.get("avg_premium_over_estimate"),
        "sell_through_rate": sentiment.get("sell_through_rate"),
        "price_trend_12m": sentiment.get("price_trend_12m"),
        "price_trend_36m": sentiment.get("price_trend_36m"),
        "sentiment_score": sentiment.get("score"),
        "sentiment_label": sentiment.get("label"),
        "notes": sentiment.get("notes"),
    }
    upsert_sentiment(sentiment_db)

    return {
        "reference": reference,
        "brand": brand,
        **sentiment,
        "calculation_date": today,
    }


# ---------------------------------------------------------------------------
# Record d'asta
# ---------------------------------------------------------------------------

@router.get("/records")
async def get_auction_records(
    brand: str | None = Query(default=None, description="Filtra per brand"),
    limit: int = Query(default=10, ge=1, le=50),
) -> list:
    """
    I record d'asta assoluti o per brand.
    Ordinati per hammer_price_chf decrescente.
    """
    records = get_records(brand=brand, limit=limit)
    return enrich_results(records)


# ---------------------------------------------------------------------------
# Calendario aste
# ---------------------------------------------------------------------------

@router.get("/calendar")
async def get_upcoming_auctions_endpoint(
    from_date: str | None = Query(default=None, description="Data ISO YYYY-MM-DD"),
) -> list:
    """
    Prossime aste in calendario.
    Dati aggiornati a conoscenza maggio 2025.
    """
    return get_upcoming_auctions(from_date=from_date)


# ---------------------------------------------------------------------------
# Case d'aste
# ---------------------------------------------------------------------------

@router.get("/houses")
async def get_auction_houses() -> list:
    """
    Lista delle principali case d'aste con statistiche aggregate dal DB
    integrate con le info di base.
    """
    db_stats = {row["auction_house"]: row for row in get_all_auction_houses()}
    houses_info = get_auction_houses_info()

    result = []
    for house in houses_info:
        name = house["name"]
        stats = db_stats.get(name, {})
        result.append({
            **house,
            "db_stats": {
                "total_lots_in_db": stats.get("total_lots", 0),
                "first_sale_in_db": stats.get("first_sale"),
                "last_sale_in_db": stats.get("last_sale"),
                "avg_hammer_chf": stats.get("avg_hammer_chf"),
                "max_hammer_chf": stats.get("max_hammer_chf"),
                "total_sales_in_db": stats.get("total_sales", 0),
            },
        })
    return result


# ---------------------------------------------------------------------------
# Risultati recenti (feed)
# ---------------------------------------------------------------------------

@router.get("/recent")
async def get_recent_auction_results(
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Ultimi N risultati d'asta nel DB, qualsiasi referenza."""
    results = get_recent_results(limit=limit)
    return {
        "total_in_db": count_results(),
        "shown": len(results),
        "results": enrich_results(results),
    }


# ---------------------------------------------------------------------------
# Scraping on-demand
# ---------------------------------------------------------------------------

@router.post("/scrape/{source}")
async def trigger_scrape(
    source: str,
    background_tasks: BackgroundTasks,
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    """
    Avvia uno scraping in background da una casa d'aste.
    source: 'phillips' | 'christies' | 'sothebys' | 'antiquorum'
    """
    source = source.lower().strip()
    valid_sources = {"phillips", "christies", "sothebys", "antiquorum"}
    if source not in valid_sources:
        raise HTTPException(
            status_code=400,
            detail=f"Source non valida. Usa: {', '.join(valid_sources)}",
        )

    async def _run_scrape(src: str, lim: int):
        logger.info(f"Scraping avviato: {src} (limit={lim})")
        try:
            if src == "phillips":
                from .scrapers.phillips_scraper import scrape_recent_results
            elif src == "christies":
                from .scrapers.christies_scraper import scrape_recent_results
            elif src == "sothebys":
                from .scrapers.sotherby_scraper import scrape_recent_results
            elif src == "antiquorum":
                from .scrapers.antiquorum_scraper import scrape_recent_results
            else:
                return

            results = await scrape_recent_results(limit=lim)
            inserted = bulk_insert_results(results)
            logger.info(f"Scraping {src}: {len(results)} lotti trovati, {inserted} inseriti nel DB")
        except Exception as e:
            logger.error(f"Scraping {src} errore: {e}")

    background_tasks.add_task(_run_scrape, source, limit)
    return {
        "status": "avviato",
        "source": source,
        "limit": limit,
        "message": f"Scraping {source} avviato in background. Controlla /auctions/recent per i risultati.",
    }


# ---------------------------------------------------------------------------
# Seed database
# ---------------------------------------------------------------------------

@router.post("/seed")
async def seed_database() -> dict:
    """
    Inserisce i dati storici seed nel database.
    Sicuro da chiamare più volte (salta duplicati).
    """
    from .seed_data import get_seed_data
    data = get_seed_data()
    inserted = bulk_insert_results(data)
    total = count_results()
    logger.info(f"Seed: {inserted} nuovi record inseriti su {len(data)} disponibili. Totale DB: {total}")
    return {
        "seed_records_available": len(data),
        "inserted": inserted,
        "skipped_duplicates": len(data) - inserted,
        "total_in_db": total,
    }


# ---------------------------------------------------------------------------
# Statistiche DB
# ---------------------------------------------------------------------------

@router.get("/stats")
async def get_auction_stats() -> dict:
    """Statistiche aggregate del database aste."""
    total = count_results()
    houses = get_all_auction_houses()
    recent = get_recent_results(limit=5)
    records = get_records(limit=3)

    return {
        "total_lots_in_db": total,
        "auction_houses": len(houses),
        "most_recent_sale": recent[0]["sale_date"] if recent else None,
        "top_records": [
            {
                "brand": r["brand"],
                "model": r["model"],
                "reference": r.get("reference"),
                "hammer_price_chf": r.get("hammer_price_chf"),
                "auction_house": r["auction_house"],
                "sale_date": r["sale_date"],
            }
            for r in records
        ],
        "houses_breakdown": [
            {"house": h["auction_house"], "lots": h["total_lots"]}
            for h in houses
        ],
    }
