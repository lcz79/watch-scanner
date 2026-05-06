"""
FastAPI router per il sistema di verifica autenticità orologi.
Prefix: /verify
"""
import base64
from fastapi import APIRouter, File, UploadFile, Query, HTTPException

from utils.logger import get_logger
from verification.report import generate_report, report_to_dict
from verification.serial_validator import validate_serial
from verification.rules_db import (
    get_rules_for_model,
    get_all_brands,
    get_models_for_brand,
)
from verification.known_fakes import find_matching_fakes, get_fake_prevalence_summary

logger = get_logger("verification.router")

router = APIRouter(prefix="/verify", tags=["verification"])


# ---------------------------------------------------------------------------
# POST /verify/analyze
# ---------------------------------------------------------------------------

@router.post("/analyze")
async def analyze_watch(
    brand: str = Query(..., description="Brand dell'orologio (es. 'Rolex', 'Patek Philippe')"),
    model: str = Query(..., description="Modello (es. 'Submariner', 'Nautilus', 'Royal Oak')"),
    reference: str | None = Query(None, description="Referenza (es. '116610LN', '5711/1A')"),
    serial_number: str | None = Query(None, description="Numero seriale inciso sull'orologio"),
    image: UploadFile | None = File(None, description="Foto dell'orologio (JPEG/PNG/WebP)"),
) -> dict:
    """
    Analisi completa di autenticità: validazione seriale + analisi visiva GPT-4o + database falsi.

    **Restituisce**:
    - `overall_score`: 0-100 (100 = certamente autentico)
    - `verdict`: giudizio finale in italiano
    - `risk_level`: low | medium | high | very_high
    - `confidence`: certezza del giudizio (0.0-1.0)
    - `red_flags`: problemi rilevati
    - `green_flags`: elementi positivi
    - `recommendations`: cosa fare
    - `serial_validation`: analisi del seriale con anno stimato
    - `known_fake_patterns`: falsi noti per questo modello
    """
    brand = brand.strip()
    model = model.strip()

    if not brand or not model:
        raise HTTPException(status_code=400, detail="brand e model sono obbligatori")

    image_b64: str | None = None
    media_type: str = "image/jpeg"

    if image:
        try:
            raw = await image.read()
            if len(raw) > 20 * 1024 * 1024:  # 20 MB max
                raise HTTPException(
                    status_code=413, detail="Immagine troppo grande (max 20MB)"
                )
            image_b64 = base64.b64encode(raw).decode("utf-8")
            ct = image.content_type or "image/jpeg"
            if ct in ("image/jpeg", "image/png", "image/webp", "image/gif"):
                media_type = ct
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Errore lettura immagine: {e}")
            raise HTTPException(status_code=400, detail=f"Errore lettura immagine: {e}")

    logger.info(
        f"Richiesta analisi: {brand} {model} | ref={reference} | "
        f"serial={'si' if serial_number else 'no'} | img={'si' if image_b64 else 'no'}"
    )

    report = await generate_report(
        brand=brand,
        model=model,
        reference=reference,
        serial=serial_number,
        image_base64=image_b64,
        media_type=media_type,
    )

    return report_to_dict(report)


# ---------------------------------------------------------------------------
# GET /verify/serial/{brand}
# ---------------------------------------------------------------------------

@router.get("/serial/{brand}")
async def validate_serial_number(
    brand: str,
    serial: str = Query(..., description="Numero seriale da validare"),
) -> dict:
    """
    Valida solo il numero seriale senza immagine.

    Restituisce:
    - `is_valid_format`: il formato è corretto per il brand?
    - `estimated_year`: anno di produzione stimato
    - `year_range`: range anni [from, to]
    - `plausible`: il seriale è plausibile?
    - `notes`: note descrittive
    - `warnings`: avvisi
    """
    brand = brand.strip()
    serial = serial.strip()

    if not serial:
        raise HTTPException(status_code=400, detail="serial è obbligatorio")

    result = validate_serial(brand, serial)

    return {
        "brand": result.brand,
        "serial": serial,
        "is_valid_format": result.is_valid_format,
        "plausible": result.plausible,
        "estimated_year": result.estimated_year,
        "year_range": list(result.year_range) if result.year_range else None,
        "notes": result.notes,
        "warnings": result.warnings,
    }


# ---------------------------------------------------------------------------
# GET /verify/rules/{brand}/{model}
# ---------------------------------------------------------------------------

@router.get("/rules/{brand}/{model}")
async def get_authentication_rules(brand: str, model: str) -> dict:
    """
    Checklist di regole di autenticità per un modello specifico.

    Restituisce i check da eseguire con descrizione e segnali di falso.
    Utile come guida manuale per l'acquirente.
    """
    brand = brand.strip()
    model = model.strip()

    rules = get_rules_for_model(brand, model)

    if not rules["found"]:
        raise HTTPException(
            status_code=404,
            detail=f"Nessuna regola trovata per {brand} {model}. "
                   f"Brand supportati: {', '.join(get_all_brands())}",
        )

    # Costruisci checklist user-friendly
    checklist = []
    priority_map = {"critical": 1, "high": 2, "medium": 3}

    for rule in rules.get("general", []):
        weight = rule.get("weight", 0.1)
        priority = "critical" if weight >= 0.2 else "high" if weight >= 0.12 else "medium"
        checklist.append({
            "check": rule["check"],
            "category": "general",
            "priority": priority,
            "weight": weight,
            "description": rule["description"],
            "fake_indicators": rule.get("fake_indicators", []),
            "authentic_indicators": rule.get("authentic_indicators", []),
        })

    for rule in rules.get("model_specific", []):
        weight = rule.get("weight", 0.1)
        priority = "critical" if weight >= 0.25 else "high" if weight >= 0.15 else "medium"
        checklist.append({
            "check": rule["check"],
            "category": "model_specific",
            "priority": priority,
            "weight": weight,
            "description": rule["description"],
            "fake_indicators": rule.get("fake_indicators", []),
            "authentic_indicators": rule.get("authentic_indicators", []),
        })

    # Ordina per priorità
    checklist.sort(key=lambda x: priority_map.get(x["priority"], 3))

    return {
        "brand": rules["brand"],
        "model": rules["model"],
        "references": rules.get("references", []),
        "total_checks": len(checklist),
        "critical_checks": sum(1 for c in checklist if c["priority"] == "critical"),
        "checklist": checklist,
        "serial_ranges": rules.get("serial_ranges", {}),
    }


# ---------------------------------------------------------------------------
# GET /verify/known-fakes/{brand}
# ---------------------------------------------------------------------------

@router.get("/known-fakes/{brand}")
async def get_known_fakes(
    brand: str,
    model: str | None = Query(None, description="Filtra per modello specifico (opzionale)"),
) -> dict:
    """
    Database falsi noti per brand e opzionalmente modello.

    Include:
    - Descrizione del falso
    - Come identificarlo
    - Prevalenza nel mercato
    - Visual tells (segnali visivi)
    """
    brand = brand.strip()

    fakes = find_matching_fakes(brand, model)
    prevalence = get_fake_prevalence_summary(brand, model)

    if not fakes and model:
        # Prova a restituire tutti i falsi del brand se il modello non ha match
        all_brand_fakes = find_matching_fakes(brand)
        if not all_brand_fakes:
            raise HTTPException(
                status_code=404,
                detail=f"Nessun falso documentato trovato per {brand}",
            )

    return {
        "brand": brand,
        "model": model,
        "total_patterns": len(fakes),
        "risk_summary": prevalence,
        "patterns": fakes,
    }


# ---------------------------------------------------------------------------
# GET /verify/brands
# ---------------------------------------------------------------------------

@router.get("/brands")
async def list_supported_brands() -> dict:
    """
    Lista di tutti i brand e modelli supportati nel sistema di verifica.
    """
    brands = get_all_brands()
    result = {}
    for b in brands:
        models = get_models_for_brand(b)
        result[b] = models

    return {
        "total_brands": len(brands),
        "brands": result,
    }
