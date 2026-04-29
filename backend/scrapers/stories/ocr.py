"""
OCR + parsing pipeline per screenshot di Instagram Stories.
Step A: OCR con pytesseract (testo sovrapposto sull'immagine)
Step B: parsing regex per prezzo, brand, referenza, keywords
Step C: strutturazione risultato
"""
import re
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("stories.ocr")

# ── Regex ──────────────────────────────────────────────────────────────────────

PRICE_RE = re.compile(
    r'(?:prezzo|price|vendesi|vendo|asking|sale|chf|euro?)\s*[:\-]?\s*[€$£]?\s*([\d\.,]{3,8})'
    r'|[€$£]\s*([\d\.,]{3,8})'
    r'|([\d]{4,6}(?:[.,]\d{3})?)\s*[€$£]'
    r'|([\d]{2,3}[.,]\d{3})\s*(?:euro?|eur\b)'
    # Fallback: formato europeo XX.XXX o XXX.XXX (OCR perde spesso il simbolo €)
    r'|(\d{2,3}[.]\d{3})\b',
    re.IGNORECASE,
)

BRAND_KEYWORDS = {
    "rolex": ["rolex", "rlx", "op 41", "op 36", "op 31", "oyster perpetual", "submariner", "daytona", "datejust", "gmt-master", "explorer"],
    "patek": ["patek", "patek philippe", "pp"],
    "audemars": ["audemars", "ap ", "royal oak", "a.p."],
    "omega": ["omega", "speedmaster", "seamaster"],
    "tudor": ["tudor", "black bay", "pelagos"],
    "breitling": ["breitling", "navitimer", "superocean"],
    "iwc": ["iwc", "portugieser", "portofino"],
    "cartier": ["cartier", "santos", "tank"],
    "hublot": ["hublot", "big bang"],
    "panerai": ["panerai", "luminor", "radiomir"],
}

REFERENCE_RE = re.compile(
    r'\b('
    r'[A-Z]{1,4}[\s\-]?\d{3,6}[A-Z0-9]{0,6}'  # PAM00441, IW3777
    r'|\d{4,6}[A-Z]{0,4}\d{0,3}'              # 116610LN
    r'|\d{4,6}[/\\]\d[A-Z]?'                  # 5711/1A
    r')\b',
    re.IGNORECASE,
)

CONDITION_KEYWORDS = {
    "new": ["nuovo", "new", "unworn", "never worn", "neuf"],
    "mint": ["mint", "ottimo", "perfetto", "like new", "pristine"],
    "good": ["buone condizioni", "good", "usato poco", "poco usato"],
    "full_set": ["full set", "scatola e garanzia", "box and papers", "completo", "con scatola"],
}

WATCH_SIGNALS = [
    "orologio", "orologi", "watch", "timepiece", "chrono", "automatic", "automatico",
    "dial", "quadrante", "acciaio", "steel", "oro", "gold",
    "fullset", "full set", "papers", "carte", "garanzia", "warranty",
    "ref.", "ref .", "referenza", "reference",
    "nuovo", "nuovi", "usato", "vintage", "mm", "41mm", "40mm", "36mm",
    "oyster", "submariner", "datejust", "daytona", "gmt", "speedmaster",
    "nautilus", "royal oak", "black bay", "explorer",
]


def _parse_price(text: str) -> float | None:
    for m in PRICE_RE.finditer(text):
        raw = next((g for g in m.groups() if g), None)
        if not raw:
            continue
        # Normalizza: 25.000 → 25000, 25,000 → 25000
        raw = raw.strip()
        if re.match(r'^\d{2,3}[.,]\d{3}$', raw):
            # formato europeo migliaia: 25.000 o 25,000
            raw = raw.replace('.', '').replace(',', '')
        else:
            raw = raw.replace('.', '').replace(',', '.')
        try:
            price = float(raw)
            if 500 < price < 500_000:
                return price
        except ValueError:
            continue
    return None


def _detect_brand(text: str) -> str | None:
    text_lower = text.lower()
    for brand, keywords in BRAND_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return brand
    return None


def _detect_reference(text: str) -> str | None:
    m = REFERENCE_RE.search(text)
    return m.group(0) if m else None


def _detect_condition(text: str) -> str:
    text_lower = text.lower()
    for condition, keywords in CONDITION_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return condition
    return "unknown"


def _is_watch_related(text: str) -> bool:
    text_lower = text.lower()
    return any(sig in text_lower for sig in WATCH_SIGNALS)


def _normalize_ocr_text(text: str) -> str:
    """
    Normalizza output OCR comune: corregge errori frequenti di riconoscimento.
    Es: virgola letta come punto-e-virgola (11.500;00€ → 11.500,00€)
    """
    # Semicolone tra cifre → virgola (OCR confonde "," con ";")
    import re as _re
    text = _re.sub(r'(\d);(\d)', r'\1,\2', text)
    # "S€" o "5€" finale dove la S è uno 0 — lascia per ora
    return text


def ocr_image(image_path: str) -> str:
    """Esegue OCR sull'immagine e ritorna il testo estratto."""
    try:
        import pytesseract
        from PIL import Image, ImageFilter, ImageEnhance

        img = Image.open(image_path)

        # Pre-processing: aumenta contrasto per testo su sfondi colorati/scuri
        img = img.convert("RGB")
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # OCR con configurazione ottimizzata per testo sparso su immagine
        text = pytesseract.image_to_string(
            img,
            lang="ita+eng",
            config="--psm 11 --oem 3",
        )
        return _normalize_ocr_text(text.strip())
    except ImportError:
        logger.debug("pytesseract non installato — OCR disabilitato")
        return ""
    except Exception as e:
        logger.debug(f"OCR error {image_path}: {e}")
        return ""


def parse_frame(
    screenshot_path: str,
    raw_page_text: str,
    username: str,
    timestamp: str,
    post_url: str = "",
) -> dict | None:
    """
    Processa un frame (screenshot + testo pagina) ed estrae dati strutturati.
    Ritorna None se il frame non contiene un listing valido.
    """
    # Combina OCR immagine + testo pagina (IG mostra parte del testo nell'HTML)
    ocr_text = ocr_image(screenshot_path)
    combined = f"{ocr_text}\n{raw_page_text}"

    # Validazione: deve essere orologio-related
    if not _is_watch_related(combined) and not _is_watch_related(raw_page_text):
        return None

    # Estrai prezzo
    price = _parse_price(combined) or _parse_price(raw_page_text)
    if not price:
        return None

    # Estrai brand e referenza
    brand = _detect_brand(combined)
    reference = _detect_reference(combined)
    condition = _detect_condition(combined)

    # Confidence score: più segnali trovati → più affidabile
    confidence = 0.3  # base
    if brand:
        confidence += 0.2
    if reference:
        confidence += 0.3
    if ocr_text:
        confidence += 0.1
    if condition != "unknown":
        confidence += 0.1
    confidence = min(1.0, confidence)

    # Testo raw pulito (rimuovi rumore)
    text_raw = " ".join(combined.split())[:300]

    return {
        "source": "instagram_story",
        "username": username,
        "price": price,
        "currency": "EUR",
        "brand": brand,
        "reference": reference,
        "condition": condition,
        "text_raw": text_raw,
        "image_path": screenshot_path,
        "post_url": post_url,
        "timestamp": timestamp,
        "confidence": round(confidence, 2),
        "ocr_text": ocr_text[:500],
    }
