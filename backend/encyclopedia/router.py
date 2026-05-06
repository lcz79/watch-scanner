"""
FastAPI router per l'enciclopedia degli orologi di lusso.
Prefix: /encyclopedia
"""
from fastapi import APIRouter, HTTPException, Query

from utils.logger import get_logger
from .database import (
    init_db, search_watches, get_watch_by_reference,
    get_brand_catalog, get_popular_references, get_all_brands, count_watches,
    insert_watch, insert_story, insert_image, insert_variant,
)

logger = get_logger("encyclopedia")

router = APIRouter(prefix="/encyclopedia", tags=["encyclopedia"])

# Initialize DB on import
try:
    init_db()
except Exception as e:
    logger.warning(f"Encyclopedia DB init warning: {e}")


@router.get("/search")
async def search_encyclopedia(
    brand: str | None = Query(None),
    model: str | None = Query(None),
    reference: str | None = Query(None),
    collection: str | None = Query(None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict:
    """Ricerca orologi nell'enciclopedia con filtri multipli."""
    results = search_watches(
        brand=brand, model=model, reference=reference,
        collection=collection, limit=limit, offset=offset,
    )
    all_brands = get_all_brands()
    total = count_watches()

    return {
        "watches": results,
        "total": total,
        "returned": len(results),
        "brands": all_brands,
    }


@router.get("/reference/{reference}")
async def get_watch_detail(reference: str) -> dict:
    """Dettaglio completo di un orologio (con storie, immagini, varianti)."""
    reference = reference.strip()
    watch = get_watch_by_reference(reference)
    if not watch:
        raise HTTPException(
            status_code=404,
            detail=f"Orologio '{reference}' non trovato nell'enciclopedia. "
                   f"Esegui POST /encyclopedia/seed per popolare il database.",
        )
    return watch


@router.get("/brand/{brand}")
async def get_brand_watches(brand: str) -> dict:
    """Tutti gli orologi di un brand."""
    brand = brand.strip()
    watches = get_brand_catalog(brand)
    return {
        "brand": brand,
        "watches": watches,
        "total": len(watches),
    }


@router.get("/popular")
async def get_popular_watches(limit: int = Query(default=20, ge=1, le=100)) -> list:
    """Referenze più importanti (ordinati per notorietà)."""
    return get_popular_references(limit=limit)


@router.get("/brands")
async def list_brands() -> list:
    """Lista tutti i brand presenti nell'enciclopedia."""
    return get_all_brands()


@router.get("/stats")
async def get_stats() -> dict:
    """Statistiche del database enciclopedia."""
    total = count_watches()
    brands = get_all_brands()
    return {
        "total_watches": total,
        "total_brands": len(brands),
        "brands": brands,
    }


@router.post("/seed")
async def seed_encyclopedia() -> dict:
    """
    Popola il database con i dati seed (200+ orologi di lusso).
    Sicuro da chiamare più volte — salta i duplicati.
    """
    try:
        from .seed_data import get_seed_data
        watches = get_seed_data()
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="seed_data.py non ancora disponibile. Il database si popola automaticamente con i dati di Wikipedia e brand websites.",
        )

    inserted = 0
    skipped = 0
    for w in watches:
        try:
            is_new = insert_watch(w)
            if is_new:
                inserted += 1
                # Insert associated stories
                for story in w.get("stories", []):
                    insert_story(
                        reference=w["reference"],
                        category=story.get("category"),
                        title=story["title"],
                        content=story["content"],
                        source_url=story.get("source_url"),
                    )
                # Insert images
                for i, img_url in enumerate(w.get("images", [])):
                    insert_image(
                        reference=w["reference"],
                        url=img_url,
                        source="official",
                        is_primary=(i == 0),
                    )
                # Insert variants
                for variant_ref in w.get("variants", []):
                    insert_variant(w["reference"], variant_ref)
            else:
                skipped += 1
        except Exception as e:
            logger.warning(f"Seed error for {w.get('reference', '?')}: {e}")

    total = count_watches()
    logger.info(f"Encyclopedia seed: {inserted} inseriti, {skipped} saltati. Totale: {total}")

    return {
        "seed_records_available": len(watches),
        "inserted": inserted,
        "skipped_duplicates": skipped,
        "total_in_db": total,
    }


@router.post("/watch")
async def add_watch(data: dict) -> dict:
    """Aggiunge o aggiorna manualmente un orologio nell'enciclopedia."""
    if not data.get("reference") or not data.get("brand") or not data.get("model"):
        raise HTTPException(status_code=400, detail="reference, brand e model sono obbligatori")

    is_new = insert_watch(data)

    return {
        "reference": data["reference"],
        "action": "created" if is_new else "updated",
    }
