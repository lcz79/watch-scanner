"""
Account Classifier.

Classifica se un account Instagram è un dealer di orologi
usando keyword matching e (opzionalmente) Claude Haiku via API Anthropic.
"""

import json

from utils.logger import get_logger
from agents.discovery import resellers_db as db_module

logger = get_logger("discovery.classifier")

# ---------------------------------------------------------------------------
# Keyword lists
# ---------------------------------------------------------------------------

KEYWORD_DEALER = [
    "for sale", "vendesi", "vendo", "dealer", "reseller",
    "buy", "price", "dm for price", "€", "orologio", "watch",
    "rolex", "patek", "audemars", "rivenditore", "acquisto", "permute",
]

KEYWORD_NOT_DEALER = [
    "fanpage", "fan account", "news", "blog", "magazine",
    "inspiration", "lifestyle only",
]

# ---------------------------------------------------------------------------
# Anthropic import (opzionale)
# ---------------------------------------------------------------------------

try:
    import anthropic as _anthropic_lib
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic SDK non disponibile — classificazione LLM disabilitata.")

CLAUDE_MODEL = "claude-haiku-4-5-20251001"


# ---------------------------------------------------------------------------
# Funzioni pubbliche
# ---------------------------------------------------------------------------

def classify_by_keywords(bio: str, captions: list[str]) -> dict:
    """
    Classifica l'account tramite keyword matching su bio e caption.

    Returns:
        {"is_dealer": bool, "confidence": float, "method": "keywords"}
    """
    combined = " ".join([bio or ""] + (captions or [])).lower()

    dealer_hits = [kw for kw in KEYWORD_DEALER if kw in combined]
    not_dealer_hits = [kw for kw in KEYWORD_NOT_DEALER if kw in combined]

    # Penalità per keyword "non dealer"
    raw_score = len(dealer_hits) - (len(not_dealer_hits) * 2)

    if raw_score <= 0:
        confidence = max(0.0, 0.3 - (len(not_dealer_hits) * 0.1))
        is_dealer = False
    elif raw_score == 1:
        confidence = 0.5
        is_dealer = False
    elif raw_score == 2:
        confidence = 0.65
        is_dealer = True
    elif raw_score == 3:
        confidence = 0.75
        is_dealer = True
    else:
        # 4+ keyword dealer → alta confidence
        confidence = min(0.95, 0.75 + (raw_score - 3) * 0.05)
        is_dealer = True

    logger.debug(
        f"[keywords] dealer_hits={dealer_hits[:3]}, not_dealer={not_dealer_hits}, "
        f"is_dealer={is_dealer}, confidence={confidence:.2f}"
    )
    return {"is_dealer": is_dealer, "confidence": confidence, "method": "keywords"}


async def classify_by_llm(bio: str, captions: list[str], api_key: str) -> dict:
    """
    Classifica tramite Claude Haiku (Anthropic API).

    Se api_key è assente o l'SDK non è disponibile, ritorna risultato neutro.

    Returns:
        {"is_dealer": bool | None, "confidence": float, "method": "llm" | "unavailable"}
    """
    _unavailable = {"is_dealer": None, "confidence": 0.0, "method": "unavailable"}

    if not api_key or not _ANTHROPIC_AVAILABLE:
        return _unavailable

    # Usa solo le prime 3 caption per contenere i costi
    captions_sample = (captions or [])[:3]
    captions_text = "\n".join(f"- {c[:200]}" for c in captions_sample) or "(nessuna caption)"

    prompt = (
        "Sei un esperto del mercato degli orologi di lusso.\n"
        "Analizza la bio e le caption di un account Instagram e dimmi se è un dealer/reseller di orologi.\n\n"
        f"BIO:\n{(bio or '').strip()[:400]}\n\n"
        f"CAPTION RECENTI:\n{captions_text}\n\n"
        "Rispondi SOLO con un oggetto JSON valido, nessun testo aggiuntivo:\n"
        '{"is_dealer": true|false, "confidence": 0.0-1.0}'
    )

    try:
        client = _anthropic_lib.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=64,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        data = json.loads(raw)
        result = {
            "is_dealer": bool(data.get("is_dealer")),
            "confidence": float(data.get("confidence", 0.5)),
            "method": "llm",
        }
        logger.debug(f"[llm] is_dealer={result['is_dealer']}, confidence={result['confidence']:.2f}")
        return result

    except json.JSONDecodeError as e:
        logger.warning(f"[llm] JSON non valido nella risposta: {e}")
        return _unavailable
    except Exception as e:
        logger.warning(f"[llm] Chiamata API fallita: {e}")
        return _unavailable


async def classify_account(
    username: str,
    bio: str,
    captions: list[str],
    api_key: str = None,
) -> dict:
    """
    Pipeline di classificazione combinata:
      1. Prova keyword matching.
      2. Se confidence < 0.8, prova LLM (se api_key disponibile).
      3. Salva il risultato nel DB.

    Returns:
        {"is_dealer": bool | None, "confidence": float, "method": str}
    """
    keyword_result = classify_by_keywords(bio, captions)

    if keyword_result["confidence"] >= 0.8:
        result = keyword_result
        logger.debug(f"[@{username}] Keyword sufficienti (conf={result['confidence']:.2f})")
    elif api_key:
        llm_result = await classify_by_llm(bio, captions, api_key)
        if llm_result["method"] == "llm":
            result = llm_result
            logger.debug(f"[@{username}] LLM usato (conf={result['confidence']:.2f})")
        else:
            # LLM non disponibile — ricade su keywords
            result = keyword_result
    else:
        result = keyword_result

    # Persisti nel DB
    _save_classification(username, bio, result)

    return result


# ---------------------------------------------------------------------------
# Helper privato
# ---------------------------------------------------------------------------

def _save_classification(username: str, bio: str, result: dict):
    """
    Aggiorna il DB con la classificazione.
    - is_dealer=True + confidence sufficiente → add_reseller
    - is_dealer=False → blacklist
    - is_dealer=None → nessuna azione
    """
    if result.get("is_dealer") is None:
        return

    db = db_module.load()

    if db_module.is_known(db, username):
        db_module.save(db)
        return

    if result["is_dealer"] and result.get("confidence", 0) >= 0.5:
        score = int(result["confidence"] * 10)
        db_module.add_reseller(
            db,
            username=username,
            platform="instagram",
            score=score,
            reasons=[f"classifier:{result['method']}:{result['confidence']:.2f}"],
            followers=0,
            bio=bio,
            discovered_via=f"classifier/{result['method']}",
            pk="",
        )
    else:
        db_module.blacklist(db, username)

    db_module.save(db)
