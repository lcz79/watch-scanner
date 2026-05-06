"""
Generazione report di autenticità combinando:
- Validazione seriale
- Analisi visiva GPT-4o
- Database falsi noti
- Regole di autenticità brand-specific
"""
from dataclasses import dataclass, field
from utils.logger import get_logger
from config import get_settings
from verification.serial_validator import validate_serial, SerialValidationResult
from verification.visual_analyzer import analyze_watch_authenticity, score_visual_result
from verification.known_fakes import find_matching_fakes, get_fake_prevalence_summary
from verification.rules_db import get_rules_for_model

logger = get_logger("verification.report")


@dataclass
class AuthenticityReport:
    brand: str
    model: str
    reference: str | None

    # --- Serial analysis ---
    serial_number: str | None
    serial_validation: SerialValidationResult | None

    # --- Visual analysis ---
    visual_score: float          # 0-100
    visual_verdict: str          # "Probabile autentico" | "Elementi sospetti" | "Probabilmente falso" | "Non determinabile"
    red_flags: list[str]         # elementi problematici
    green_flags: list[str]       # elementi positivi
    visual_checks: list[dict]    # dettaglio check individuali

    # --- Overall ---
    overall_score: float         # 0-100 (weighted average)
    verdict: str                 # verdetto finale in italiano
    confidence: float            # 0.0-1.0 — quanto siamo certi del verdetto
    risk_level: str              # "low" | "medium" | "high" | "very_high"

    # --- Detailed checks ---
    checks_passed: list[str]
    checks_failed: list[str]
    checks_warning: list[str]

    # --- Recommendations ---
    recommendations: list[str]

    # --- Known fakes ---
    matches_known_fake: bool
    known_fake_patterns: list[dict]
    known_fake_notes: str | None

    # --- Analysis metadata ---
    analysis_method: str  # "gpt4o_vision" | "rules_only" | "serial_only"
    rules_available: bool


# ---------------------------------------------------------------------------
# Pesi per il calcolo dello score finale
# ---------------------------------------------------------------------------
_WEIGHT_VISUAL = 0.55        # analisi visiva GPT-4o
_WEIGHT_SERIAL = 0.25        # validazione seriale
_WEIGHT_KNOWN_FAKE = 0.20    # match nel database falsi noti


def _serial_to_score(validation: SerialValidationResult | None) -> float:
    """Converte la validazione seriale in uno score 0-100."""
    if validation is None:
        return 50.0  # nessun seriale → neutro

    if not validation.is_valid_format:
        return 10.0  # seriale invalido → forte segnale negativo

    if not validation.plausible:
        return 20.0  # formato ok ma non plausibile → segnale negativo

    # Seriale valido e plausibile: score base alto
    score = 80.0

    # Riduzione per warnings
    score -= len(validation.warnings) * 10.0

    return max(0.0, min(100.0, score))


def _known_fake_to_score(matches: list[dict]) -> float:
    """Converte i match con falsi noti in uno score 0-100."""
    if not matches:
        return 75.0  # nessun match → leggermente positivo (ma non conclusivo)

    # Penalizza in base alla prevalenza dei falsi trovati
    very_common = sum(1 for m in matches if m.get("prevalence") == "very_common")
    common = sum(1 for m in matches if m.get("prevalence") == "common")

    penalty = very_common * 20 + common * 10
    return max(0.0, 60.0 - penalty)


def _compute_overall(
    visual_score: float,
    serial_score: float,
    known_fake_score: float,
    has_image: bool,
    has_serial: bool,
) -> tuple[float, float]:
    """
    Calcola overall score e confidence.
    Aggiusta i pesi dinamicamente in base a cosa è disponibile.
    Returns (overall_score, confidence)
    """
    if has_image and has_serial:
        w_vis, w_ser, w_fake = 0.55, 0.25, 0.20
        confidence_base = 0.75
    elif has_image and not has_serial:
        w_vis, w_ser, w_fake = 0.70, 0.0, 0.30
        confidence_base = 0.55
    elif not has_image and has_serial:
        w_vis, w_ser, w_fake = 0.0, 0.60, 0.40
        confidence_base = 0.45
    else:
        # Solo database falsi
        w_vis, w_ser, w_fake = 0.0, 0.0, 1.0
        confidence_base = 0.20

    overall = (
        visual_score * w_vis
        + serial_score * w_ser
        + known_fake_score * w_fake
    )
    return round(overall, 1), round(confidence_base, 2)


def _score_to_verdict(score: float, confidence: float) -> tuple[str, str]:
    """
    Converte score e confidence in verdetto e risk level.
    Returns (verdict, risk_level)
    """
    if confidence < 0.3:
        return "Verifica insufficiente — necessaria ispezione fisica", "unknown"

    if score >= 80:
        return "Probabile autentico", "low"
    elif score >= 65:
        return "Probabile autentico con alcune incertezze", "low"
    elif score >= 50:
        return "Elementi sospetti — ispezione fisica raccomandata", "medium"
    elif score >= 35:
        return "Probabilmente non autentico", "high"
    else:
        return "Quasi certamente falso", "very_high"


def _build_recommendations(
    verdict: str,
    risk_level: str,
    serial_validation: SerialValidationResult | None,
    red_flags: list[str],
    known_fake_patterns: list[dict],
    brand: str,
    model: str,
) -> list[str]:
    """Costruisce la lista di raccomandazioni personalizzate."""
    recs = []

    if risk_level in ("high", "very_high"):
        recs.append(
            f"NON ACQUISTARE senza verifica fisica da un rivenditore autorizzato {brand} "
            f"o da un orologiaio specializzato."
        )
        recs.append(
            "Richiedi al venditore documenti originali: certificato di garanzia, "
            "scatola originale con seriale corrispondente, fattura di acquisto."
        )
    elif risk_level == "medium":
        recs.append(
            "Procedi con cautela. Richiedi ispezione fisica prima dell'acquisto."
        )
        recs.append(
            "Verifica il numero seriale sul sito/archivi del brand se disponibile."
        )

    if serial_validation:
        if not serial_validation.is_valid_format:
            recs.append(
                f"Il numero seriale '{serial_validation.brand}' ha formato non valido. "
                "Un seriale non valido è un forte indicatore di falso."
            )
        elif serial_validation.estimated_year:
            recs.append(
                f"Il seriale corrisponde a produzione circa {serial_validation.estimated_year}. "
                "Verifica che il modello fisico corrisponda a quel periodo di produzione."
            )

    if red_flags:
        recs.append(
            f"Sono stati rilevati {len(red_flags)} segnali d'allarme visivi: "
            + "; ".join(red_flags[:3])
            + ("..." if len(red_flags) > 3 else "")
            + "."
        )

    if known_fake_patterns:
        very_common_fakes = [p for p in known_fake_patterns if p.get("prevalence") == "very_common"]
        if very_common_fakes:
            recs.append(
                f"Questo modello ha {len(very_common_fakes)} falsi molto diffusi nel mercato. "
                "Confronta attentamente con le immagini originali prima di procedere."
            )

    if risk_level == "low":
        recs.append(
            "L'orologio mostra indicatori di autenticità. "
            "Per acquisti sopra i 5.000€ si consiglia comunque una perizia fisica."
        )

    if not recs:
        recs.append(
            "Dati insufficienti per una valutazione completa. "
            "Fornire immagini ad alta risoluzione e numero seriale per un'analisi più accurata."
        )

    return recs


async def generate_report(
    brand: str,
    model: str,
    reference: str | None = None,
    serial: str | None = None,
    image_base64: str | None = None,
    media_type: str = "image/jpeg",
) -> AuthenticityReport:
    """
    Genera un report completo di autenticità.
    Combina:
    1. Validazione seriale
    2. Analisi visiva GPT-4o (se immagine + API key disponibili)
    3. Database falsi noti
    4. Regole brand-specific
    """
    settings = get_settings()
    logger.info(f"Avvio analisi autenticità: {brand} {model} | ref={reference} | serial={'si' if serial else 'no'} | img={'si' if image_base64 else 'no'}")

    # --- 1. Validazione seriale ---
    serial_validation: SerialValidationResult | None = None
    if serial and serial.strip():
        serial_validation = validate_serial(brand, serial.strip())
        logger.debug(
            f"Seriale {serial}: valid={serial_validation.is_valid_format}, "
            f"year={serial_validation.estimated_year}"
        )

    # --- 2. Analisi visiva ---
    visual_result: dict = {}
    if image_base64:
        visual_result = await analyze_watch_authenticity(
            image_base64=image_base64,
            brand=brand,
            model=model,
            reference=reference,
            media_type=media_type,
            openai_api_key=settings.openai_api_key,
        )
    else:
        visual_result = {
            "overall_authenticity": "unknown",
            "confidence": 0.0,
            "checks": [],
            "red_flags": [],
            "green_flags": [],
            "recommendation": "Nessuna immagine fornita per l'analisi visiva.",
            "analysis_method": "rules_only",
        }

    visual_score, visual_verdict = score_visual_result(visual_result)
    red_flags: list[str] = visual_result.get("red_flags", [])
    green_flags: list[str] = visual_result.get("green_flags", [])
    visual_checks: list[dict] = visual_result.get("checks", [])

    # --- 3. Database falsi noti ---
    known_fake_patterns = find_matching_fakes(brand, model)
    matches_known_fake = len(known_fake_patterns) > 0
    fake_prevalence = get_fake_prevalence_summary(brand, model)

    known_fake_notes: str | None = None
    if known_fake_patterns:
        very_common = [p for p in known_fake_patterns if p.get("prevalence") == "very_common"]
        if very_common:
            known_fake_notes = (
                f"{brand} {model} è tra i modelli più falsificati sul mercato. "
                f"Trovati {len(very_common)} pattern di falsi molto diffusi."
            )
        else:
            known_fake_notes = f"Trovati {len(known_fake_patterns)} pattern di falsi documentati per questo modello."

    # --- 4. Check dettagliati dai risultati visivi ---
    checks_passed = [
        c["check_name"] for c in visual_checks if c.get("result") == "pass"
    ]
    checks_failed = [
        c["check_name"] for c in visual_checks if c.get("result") == "fail"
    ]
    checks_warning = [
        c["check_name"] for c in visual_checks if c.get("result") == "warning"
    ]

    # Aggiungi serial check ai check lists
    if serial_validation:
        if serial_validation.is_valid_format and serial_validation.plausible:
            checks_passed.append("serial_format")
        elif not serial_validation.is_valid_format:
            checks_failed.append("serial_format")
            red_flags.append(f"Seriale non valido: {serial_validation.notes}")
        else:
            checks_warning.append("serial_format")

    # --- 5. Score finale ---
    serial_score = _serial_to_score(serial_validation)
    known_fake_score = _known_fake_to_score(known_fake_patterns)

    overall_score, confidence = _compute_overall(
        visual_score=visual_score,
        serial_score=serial_score,
        known_fake_score=known_fake_score,
        has_image=bool(image_base64),
        has_serial=bool(serial),
    )

    verdict, risk_level = _score_to_verdict(overall_score, confidence)

    # Aumenta confidence se abbiamo sia immagine che seriale e concordano
    if image_base64 and serial:
        visual_auth = visual_result.get("overall_authenticity", "unknown")
        serial_ok = serial_validation and serial_validation.is_valid_format and serial_validation.plausible
        if visual_auth == "likely_authentic" and serial_ok:
            confidence = min(0.92, confidence + 0.15)
        elif visual_auth == "likely_fake" and not serial_ok:
            confidence = min(0.92, confidence + 0.10)

    # --- 6. Regole disponibili ---
    rules_info = get_rules_for_model(brand, model)
    rules_available = rules_info["found"]

    # --- 7. Raccomandazioni ---
    recommendations = _build_recommendations(
        verdict=verdict,
        risk_level=risk_level,
        serial_validation=serial_validation,
        red_flags=red_flags,
        known_fake_patterns=known_fake_patterns,
        brand=brand,
        model=model,
    )

    analysis_method = visual_result.get("analysis_method", "rules_only")

    logger.info(
        f"Report completato: {brand} {model} | score={overall_score} | "
        f"verdict='{verdict}' | confidence={confidence:.2f} | method={analysis_method}"
    )

    return AuthenticityReport(
        brand=brand,
        model=model,
        reference=reference,
        serial_number=serial,
        serial_validation=serial_validation,
        visual_score=visual_score,
        visual_verdict=visual_verdict,
        red_flags=red_flags,
        green_flags=green_flags,
        visual_checks=visual_checks,
        overall_score=overall_score,
        verdict=verdict,
        confidence=round(confidence, 2),
        risk_level=risk_level,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        checks_warning=checks_warning,
        recommendations=recommendations,
        matches_known_fake=matches_known_fake,
        known_fake_patterns=known_fake_patterns[:5],  # max 5 per non appesantire la response
        known_fake_notes=known_fake_notes,
        analysis_method=analysis_method,
        rules_available=rules_available,
    )


def report_to_dict(report: AuthenticityReport) -> dict:
    """Serializza AuthenticityReport in dict JSON-serializzabile."""
    serial_val = None
    if report.serial_validation:
        sv = report.serial_validation
        serial_val = {
            "is_valid_format": sv.is_valid_format,
            "estimated_year": sv.estimated_year,
            "year_range": list(sv.year_range) if sv.year_range else None,
            "brand": sv.brand,
            "notes": sv.notes,
            "warnings": sv.warnings,
            "plausible": sv.plausible,
        }

    return {
        "brand": report.brand,
        "model": report.model,
        "reference": report.reference,
        "serial_number": report.serial_number,
        "serial_validation": serial_val,
        "visual_score": report.visual_score,
        "visual_verdict": report.visual_verdict,
        "red_flags": report.red_flags,
        "green_flags": report.green_flags,
        "visual_checks": report.visual_checks,
        "overall_score": report.overall_score,
        "verdict": report.verdict,
        "confidence": report.confidence,
        "risk_level": report.risk_level,
        "checks_passed": report.checks_passed,
        "checks_failed": report.checks_failed,
        "checks_warning": report.checks_warning,
        "recommendations": report.recommendations,
        "matches_known_fake": report.matches_known_fake,
        "known_fake_patterns": report.known_fake_patterns,
        "known_fake_notes": report.known_fake_notes,
        "analysis_method": report.analysis_method,
        "rules_available": report.rules_available,
    }
