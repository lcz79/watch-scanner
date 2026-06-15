from fastapi import APIRouter, HTTPException, Query

from .engine import check_coevality, list_references
from .models import CoevalityResult

router = APIRouter(prefix="/coevality", tags=["coevality"])


@router.get("/references")
async def get_references() -> list[dict]:
    """Referenze supportate dal controllo coevità."""
    return list_references()


@router.get("/check", response_model=CoevalityResult)
async def check(
    serial: str = Query(..., min_length=2, description="Numero di serie, es. U543456"),
    reference: str = Query("16520", description="Referenza orologio, es. 16520"),
) -> CoevalityResult:
    """Analizza il seriale e restituisce i componenti coevi con l'anno stimato."""
    result = check_coevality(serial, reference)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Referenza '{reference}' non ancora supportata dal controllo coevità.",
        )
    return result
