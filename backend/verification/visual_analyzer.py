"""
Analisi visiva di autenticità usando GPT-4o Vision.
Fallback su analisi basata solo sulle regole testuali se OpenAI non è configurato.
"""
import json
import httpx
from utils.logger import get_logger
from verification.rules_db import get_rules_for_model

logger = get_logger("verification.visual")


def _build_rules_summary(brand: str, model: str) -> str:
    """Costruisce un testo compatto delle regole per il prompt GPT-4o."""
    rules = get_rules_for_model(brand, model)
    if not rules["found"]:
        return f"No specific rules found for {brand} {model}. Use general luxury watch authentication knowledge."

    lines = []

    if rules.get("general"):
        lines.append("GENERAL BRAND CHECKS:")
        for rule in rules["general"]:
            indicators = "; ".join(rule.get("fake_indicators", [])[:3])
            lines.append(f"  - {rule['check']}: {rule['description'][:120]}. FAKE SIGNS: {indicators}")

    if rules.get("model_specific"):
        lines.append(f"\nMODEL-SPECIFIC CHECKS ({model.upper()}):")
        for rule in rules["model_specific"]:
            indicators = "; ".join(rule.get("fake_indicators", [])[:3])
            lines.append(f"  - {rule['check']}: {rule['description'][:120]}. FAKE SIGNS: {indicators}")

    return "\n".join(lines)


async def analyze_watch_authenticity(
    image_base64: str,
    brand: str,
    model: str,
    reference: str | None = None,
    media_type: str = "image/jpeg",
    openai_api_key: str = "",
) -> dict:
    """
    Analizza un'immagine per autenticità usando GPT-4o Vision.

    Se openai_api_key è vuoto o non configurato, ritorna un'analisi placeholder
    basata solo sulle regole testuali (nessuna chiamata API).

    Returns dict con:
        overall_authenticity: "likely_authentic" | "suspicious" | "likely_fake"
        confidence: 0.0-1.0
        checks: list[dict] con check_name, result, notes
        red_flags: list[str]
        green_flags: list[str]
        recommendation: str
        analysis_method: "gpt4o_vision" | "rules_only"
    """
    rules_summary = _build_rules_summary(brand, model)
    ref_str = f" ref {reference}" if reference else ""

    if not openai_api_key:
        logger.info(f"GPT-4o non configurato — analisi visiva non disponibile per {brand} {model}")
        return _fallback_no_vision(brand, model, reference, rules_summary)

    prompt = f"""You are an expert luxury watch authentication specialist with 20+ years of experience.
Analyze this {brand} {model}{ref_str} watch image for authenticity.

Authentication checklist for this specific watch:
{rules_summary}

Carefully examine the image and check each indicator. Focus on:
1. Quality of printing/engraving on dial (font, spacing, depth)
2. Finishing quality (alternating matte/polished surfaces, sharp angles)
3. Logo quality (proportions, symmetry)
4. Visible movement through caseback if shown
5. Bracelet/strap quality and integration
6. Bezel quality (alignment, material, uniformity)
7. Overall proportions and case finishing

Return ONLY a valid JSON object with this exact structure:
{{
  "overall_authenticity": "likely_authentic" | "suspicious" | "likely_fake",
  "confidence": 0.0-1.0,
  "checks": [
    {{
      "check_name": "string",
      "result": "pass" | "fail" | "warning" | "cannot_verify",
      "notes": "brief observation"
    }}
  ],
  "red_flags": ["list of suspicious elements found"],
  "green_flags": ["list of positive authenticity indicators found"],
  "recommendation": "brief actionable recommendation in Italian"
}}

Be conservative: if image quality prevents verification of a check, mark it "cannot_verify".
If even one clear red flag is found, mark overall as at least "suspicious".
"""

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o",
                    "max_tokens": 1200,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{media_type};base64,{image_base64}",
                                        "detail": "high",
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            result = json.loads(raw) if isinstance(raw, str) else raw

            # Normalizza e aggiunge metadati
            result["analysis_method"] = "gpt4o_vision"
            result["brand"] = brand
            result["model"] = model
            result["reference"] = reference

            logger.info(
                f"GPT-4o analisi completata: {brand} {model} → "
                f"{result.get('overall_authenticity')} "
                f"(confidence={result.get('confidence', 0):.2f})"
            )
            return result

    except httpx.HTTPStatusError as e:
        logger.error(f"GPT-4o API error {e.response.status_code}: {e.response.text[:200]}")
        return _fallback_api_error(brand, model, reference, str(e))
    except json.JSONDecodeError as e:
        logger.error(f"GPT-4o JSON parse error: {e}")
        return _fallback_api_error(brand, model, reference, f"JSON parse error: {e}")
    except Exception as e:
        logger.error(f"GPT-4o analisi fallita: {e}")
        return _fallback_api_error(brand, model, reference, str(e))


def _fallback_no_vision(brand: str, model: str, reference: str | None, rules_summary: str) -> dict:
    """
    Fallback quando GPT-4o non è disponibile.
    Restituisce struttura con tutti i check non verificabili + lista dei check da fare.
    """
    rules = get_rules_for_model(brand, model)
    checks = []

    for rule in rules.get("general", []) + rules.get("model_specific", []):
        checks.append({
            "check_name": rule["check"],
            "result": "cannot_verify",
            "notes": f"Verifica manuale richiesta: {rule['description'][:100]}",
        })

    return {
        "overall_authenticity": "unknown",
        "confidence": 0.0,
        "checks": checks,
        "red_flags": [],
        "green_flags": [],
        "recommendation": (
            f"Analisi visiva AI non disponibile (API key OpenAI non configurata). "
            f"Esegui i seguenti controlli manuali per {brand} {model}."
        ),
        "analysis_method": "rules_only",
        "brand": brand,
        "model": model,
        "reference": reference,
        "manual_checklist": rules_summary,
    }


def _fallback_api_error(brand: str, model: str, reference: str | None, error: str) -> dict:
    """Fallback in caso di errore API."""
    return {
        "overall_authenticity": "unknown",
        "confidence": 0.0,
        "checks": [],
        "red_flags": [],
        "green_flags": [],
        "recommendation": "Analisi visiva AI non completata per errore tecnico. Riprovare o procedere con verifica manuale.",
        "analysis_method": "error",
        "error": error,
        "brand": brand,
        "model": model,
        "reference": reference,
    }


def score_visual_result(visual_result: dict) -> tuple[float, str]:
    """
    Converte il risultato GPT-4o in uno score numerico (0-100) e un verdetto testuale.

    Returns (score, verdict)
    """
    authenticity = visual_result.get("overall_authenticity", "unknown")
    confidence = float(visual_result.get("confidence", 0.0))
    red_flags = visual_result.get("red_flags", [])
    checks = visual_result.get("checks", [])

    if authenticity == "unknown":
        return 50.0, "Non determinabile"

    # Base score
    if authenticity == "likely_authentic":
        base = 85.0
    elif authenticity == "suspicious":
        base = 45.0
    else:  # likely_fake
        base = 15.0

    # Modifica per confidence
    score = base * (0.5 + 0.5 * confidence)

    # Penalità per red flags
    score -= len(red_flags) * 5.0

    # Bonus per check passati
    passed = sum(1 for c in checks if c.get("result") == "pass")
    failed = sum(1 for c in checks if c.get("result") == "fail")
    if passed + failed > 0:
        pass_ratio = passed / (passed + failed)
        score = score * 0.7 + (pass_ratio * 100) * 0.3

    score = max(0.0, min(100.0, score))

    if score >= 75:
        verdict = "Probabile autentico"
    elif score >= 55:
        verdict = "Elementi sospetti"
    elif score >= 35:
        verdict = "Probabilmente falso"
    else:
        verdict = "Quasi certamente falso"

    return round(score, 1), verdict
