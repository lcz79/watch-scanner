"""
OCR + parsing pipeline per screenshot di Instagram Stories.
Step A: OCR con pytesseract (testo sovrapposto sull'immagine)
Step B: parsing regex avanzato per prezzo, brand, referenza, keywords
Step C: strutturazione risultato

Regole di estrazione:
  PREZZO      — €14.500, 14500€, 14.500 eur, CHF 12000, £9500, 14500 eur trattabili
  REFERENZA   — 116610LN, 5711/1A, 15500ST.OO, 126710BLNR, 321.10.42
  DISPONIB.   — disponibile, sold, venduto, reserved
  CONDIZIONE  — full set, scatola e garanzia, papiers, box papers, solo orologio
  CONTATTO    — DM per info, whatsapp, numeri di telefono, link in bio
"""
import re
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("stories.ocr")

# ── Regex prezzo ────────────────────────────────────────────────────────────────
#
# Ordine di priorità (il primo match non-None vince):
#   1. Keyword esplicita seguita da cifre e/o simbolo valuta
#   2. Simbolo valuta prima delle cifre (€14.500, CHF12000, £9500)
#   3. Cifre seguite da simbolo valuta (14500€, 14.500eur)
#   4. Cifre seguite da "trattabili/tratt." con valuta opzionale
#   5. Fallback europeo XX.XXX / XXX.XXX senza simbolo (OCR perde spesso €)

PRICE_RE = re.compile(
    # --- Gruppo 1: keyword + cifre
    r'(?:prezzo|price|vendesi|vendo|asking|sale|chf|franco|sterling)\s*[:\-]?\s*'
    r'(?:chf|eur?o?|gbp|usd|£|\$|€)?\s*([\d]{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)'
    # --- Gruppo 2: CHF / GBP / USD prima delle cifre (senza keyword)
    r'|(?:chf|gbp|usd)\s*([\d]{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)'
    # --- Gruppo 3: € / £ / $ prima delle cifre
    r'|[€£\$]\s*([\d]{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)'
    # --- Gruppo 4: cifre + valuta dopo
    r'|([\d]{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?)\s*(?:€|£|\$|eur?o?|chf|gbp)'
    # --- Gruppo 5: cifre 4-6 digit puri + valuta
    r'|([\d]{4,6})\s*(?:€|£|\$|eur?o?)\s*(?:tratt(?:abili)?\.?)?'
    # --- Gruppo 6: fallback europeo XX.XXX o XXX.XXX
    r'|(\d{2,3}[.]\d{3})\b',
    re.IGNORECASE,
)

# ── Regex referenza ─────────────────────────────────────────────────────────────
#
# Copre i formati più comuni di tutti i brand principali:
#   Rolex       116610LN, 126710BLNR, 228235
#   Patek       5711/1A, 5726/1A-001
#   AP          15500ST.OO.1220ST.01, 26240CE.OO.1234CE.01
#   Omega       321.10.42.50.01.001, 232.30.42.21.01.001
#   IWC         IW3777-11, IW500901
#   Panerai     PAM00441, PAM 00XXX
#   Breitling   AB0162121B1S1, A17368
#   Cartier     W2SA0009, WGBB0022
#   Hublot      411.NX.1170.RX
#   Tudor       M79030N-0001, 79230N
#   Tag Heuer   CBN2A10.BA0643, WAZ2113
#   Vacheron    49145/000R-9239

REFERENCE_RE = re.compile(
    r'\b(?:'
    # Omega a punti: 321.10.42.50.01.001
    r'\d{3}[.]\d{2}[.]\d{2}[.]\d{2}[.]\d{2}[.]\d{3}'
    # Hublot/Breitling a punti: 411.NX.1170.RX
    r'|[0-9]{3}[.][A-Z]{2}[.]\d{4}[.][A-Z]{2}'
    # AP long: 15500ST.OO.1220ST.01
    r'|[0-9]{5}[A-Z]{2}[.][A-Z0-9]{2}[.]\d{4}[A-Z]{2}[.]\d{2}'
    # Patek con slash: 5711/1A-001 o 5711/1A
    r'|\d{4}[/\\]\d[A-Z]?(?:-\d{3})?'
    # Panerai: PAM00441 o PAM 441
    r'|PAM\s*\d{3,6}'
    # IWC: IW377711, IW500901
    r'|IW[0-9]{5,7}(?:-[0-9]{2})?'
    # Rolex/Tudor/Breitling: 116610LN, 79230N, A17368
    r'|[A-Z]{0,2}[0-9]{4,6}[A-Z]{0,4}[0-9]{0,3}'
    # Vacheron/Cartier: 49145/000R-9239
    r'|\d{5}[/]\d{3}[A-Z]-\d{4}'
    # Tag Heuer: CBN2A10.BA0643
    r'|[A-Z]{3}[0-9][A-Z][0-9]{2}[.][A-Z]{2}[0-9]{4}'
    r')\b',
    re.IGNORECASE,
)

# Referenze false-positive da escludere (es. numeri di telefono, date, prezzi già catturati)
_REF_BLACKLIST_RE = re.compile(
    r'^(?:\d{8,}|20\d{2}|\d{2}[/]\d{2}[/]\d{2,4}|[0-9]{1,3}[.][0-9]{3}$)$',
    re.IGNORECASE,
)

# ── Brand keywords ──────────────────────────────────────────────────────────────

BRAND_KEYWORDS: dict[str, list[str]] = {
    "rolex": [
        "rolex", "rlx", "oyster perpetual", "op 41", "op 36", "op 31", "op41", "op36",
        "submariner", "sub", "daytona", "datejust", "dj", "gmt-master", "gmt master",
        "explorer", "sea-dweller", "seadweller", "milgauss", "sky-dweller", "skydweller",
        "day-date", "daydate", "yacht-master", "yachtmaster",
    ],
    "patek": [
        "patek", "patek philippe", "pp", "nautilus", "aquanaut", "calatrava",
        "grand complications", "perpetual calendar",
    ],
    "audemars": [
        "audemars", "ap ", "a.p.", "royal oak", "royal oak offshore", "offshore",
        "code 11.59",
    ],
    "omega": [
        "omega", "speedmaster", "seamaster", "constellation", "aqua terra",
        "planet ocean", "de ville",
    ],
    "tudor": [
        "tudor", "black bay", "bb58", "bb41", "pelagos", "ranger",
        "glamour", "fastrider",
    ],
    "breitling": [
        "breitling", "navitimer", "superocean", "avenger", "chronomat",
        "premier", "transocean",
    ],
    "iwc": [
        "iwc", "portugieser", "portofino", "pilot", "ingenieur",
        "aquatimer", "da vinci",
    ],
    "cartier": [
        "cartier", "santos", "tank", "ballon bleu", "panthère", "pantera",
        "ronde", "pasha",
    ],
    "hublot": [
        "hublot", "big bang", "classic fusion", "spirit of big bang",
    ],
    "panerai": [
        "panerai", "luminor", "radiomir", "submersible", "luminor marina",
    ],
    "vacheron": [
        "vacheron", "vacheron constantin", "vc", "overseas", "traditionnelle",
        "patrimony", "historiques",
    ],
    "lange": [
        "a. lange", "lange", "lange & söhne", "datograph", "saxonia",
        "lange 1", "zeitwerk",
    ],
    "jaeger": [
        "jaeger", "jlc", "jaeger-lecoultre", "reverso", "master",
        "polaris", "atmos",
    ],
}

# ── Disponibilità ───────────────────────────────────────────────────────────────

AVAILABILITY_KEYWORDS: dict[str, list[str]] = {
    "available": [
        "disponibile", "disponible", "available", "in vendita", "for sale",
        "vendesi", "vendo", "selling", "à vendre",
    ],
    "sold": [
        "sold", "venduto", "vendu", "verkauft", "verkocht",
        "è stato venduto", "già venduto",
    ],
    "reserved": [
        "reserved", "riservato", "réservé", "reserviert", "in trattativa",
        "trattativa in corso", "on hold",
    ],
}

# ── Condizione ──────────────────────────────────────────────────────────────────

CONDITION_KEYWORDS: dict[str, list[str]] = {
    "new": [
        "nuovo", "new", "unworn", "never worn", "neuf", "neue",
        "mai indossato", "mint in box",
    ],
    "mint": [
        "mint", "ottimo", "perfetto", "like new", "pristine", "eccellente",
        "come nuovo", "praticamente nuovo",
    ],
    "good": [
        "buone condizioni", "good condition", "usato poco", "poco usato",
        "used", "usato", "getragen", "port",
    ],
    "fair": [
        "segni di usura", "graffi", "scratches", "worn", "gebraucht", "usé",
        "patina", "fair condition",
    ],
    "full_set": [
        "full set", "fullset", "scatola e garanzia", "box and papers",
        "box & papers", "completo", "con scatola", "papiers", "carte d'origine",
        "schachtel", "cofanetto", "con tutto",
    ],
    "no_papers": [
        "solo orologio", "only watch", "no box", "no papers", "senza scatola",
        "senza garanzia", "senza documenti", "nuda", "solo cassa",
    ],
}

# ── Segnali orologio ────────────────────────────────────────────────────────────

WATCH_SIGNALS = [
    # Generico
    "orologio", "orologi", "watch", "timepiece", "chrono", "chronograph",
    "automatic", "automatico", "manuale", "manual", "quarzo", "quartz",
    # Materiali e parti
    "dial", "quadrante", "acciaio", "steel", "oro", "gold", "platino", "platinum",
    "bracciale", "bracelet", "oyster", "jubilee", "leather", "pelle", "rubber",
    "vetro", "zaffiro", "sapphire", "cassa", "case", "corona",
    # Documenti
    "fullset", "full set", "papers", "carte", "garanzia", "warranty",
    "certificato", "certificate", "box", "scatola", "libretto",
    # Codici e tag vendita
    "ref.", "ref .", "referenza", "reference", "rif.", "rif ",
    "vendita", "vendo", "prezzo", "asking", "for sale",
    # Misure
    "mm", "41mm", "40mm", "36mm", "42mm", "44mm", "45mm",
    # Modelli comuni (senza brand duplice)
    "oyster", "submariner", "datejust", "daytona", "gmt", "speedmaster",
    "nautilus", "royal oak", "black bay", "explorer", "seamaster",
    "luminor", "navitimer", "big bang",
]

# ── Contatto ────────────────────────────────────────────────────────────────────

CONTACT_RE = re.compile(
    r'(?:dm|direct\s*message|messaggio\s*privato|contattami|contact(?:aci)?'
    r'|whatsapp|whats\s*app|wa[:\s]+|telegram|signal'
    r'|link\s*in\s*bio|bio\s*link'
    r'|(?:\+?[0-9]{2,3}[\s\-]?[0-9]{3,5}[\s\-]?[0-9]{3,5}[\s\-]?[0-9]{0,5})'  # telefono
    r')',
    re.IGNORECASE,
)

PHONE_RE = re.compile(
    r'(?:\+?[0-9]{2,3}[\s\-]?){2,4}[0-9]{3,5}',
)


# ── Funzioni di parsing ─────────────────────────────────────────────────────────

def _parse_price(text: str) -> float | None:
    """
    Estrae il primo prezzo plausibile dal testo.
    Gestisce formati europei (14.500), anglofoni (14,500) e misti.
    Range plausibile: 500 – 500.000 €.
    """
    for m in PRICE_RE.finditer(text):
        raw = next((g for g in m.groups() if g), None)
        if not raw:
            continue
        raw = raw.strip()

        # Determina se è formato europeo migliaia (25.000 / 25,000)
        # oppure decimali (25.50 / 25,50)
        if re.match(r'^\d{1,3}(?:[.,]\d{3})+$', raw):
            # Separatore migliaia puro → rimuovi entrambi i separatori
            raw = raw.replace('.', '').replace(',', '')
        elif re.match(r'^\d{1,3}[.,]\d{3}[.,]\d{1,2}$', raw):
            # es. 14.500,00 o 14,500.00 → mantieni solo la parte intera
            raw = re.sub(r'[.,]\d{1,2}$', '', raw)
            raw = raw.replace('.', '').replace(',', '')
        else:
            # Formato decimale standard
            raw = raw.replace('.', '').replace(',', '.')

        try:
            price = float(raw)
            if 500 < price < 500_000:
                return price
        except ValueError:
            continue
    return None


def _detect_currency(text: str) -> str:
    """Rileva la valuta principale menzionata nel testo."""
    text_lower = text.lower()
    if re.search(r'\bchf\b', text_lower):
        return "CHF"
    if re.search(r'\bgbp\b|£', text_lower):
        return "GBP"
    if re.search(r'\busd\b|\$', text_lower):
        return "USD"
    return "EUR"


def _detect_brand(text: str) -> str | None:
    text_lower = text.lower()
    for brand, keywords in BRAND_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return brand
    return None


def _detect_reference(text: str) -> str | None:
    """
    Cerca la prima referenza valida nel testo.
    Filtra i false-positive contro una blacklist di pattern.
    """
    for m in REFERENCE_RE.finditer(text):
        candidate = m.group(0).strip()
        if _REF_BLACKLIST_RE.match(candidate):
            continue
        # Deve avere almeno una cifra e almeno 4 caratteri
        if len(candidate) >= 4 and re.search(r'\d', candidate):
            return candidate
    return None


def _detect_condition(text: str) -> str:
    """
    Ritorna la condizione con la maggiore priorità trovata.
    Ordine di priorità: new > mint > good > fair > full_set > no_papers > unknown.
    """
    text_lower = text.lower()
    for condition in ("new", "mint", "good", "fair"):
        if any(kw in text_lower for kw in CONDITION_KEYWORDS[condition]):
            return condition

    # Condizioni di set (non mutualmente esclusive con le sopra)
    has_full_set = any(kw in text_lower for kw in CONDITION_KEYWORDS["full_set"])
    has_no_papers = any(kw in text_lower for kw in CONDITION_KEYWORDS["no_papers"])

    if has_full_set:
        return "mint"   # full set tende a indicare ottima conservazione
    if has_no_papers:
        return "good"   # solo orologio → condizione non peggiore di good

    return "unknown"


def _detect_availability(text: str) -> str:
    """Rileva disponibilità: available / sold / reserved / unknown."""
    text_lower = text.lower()
    for status, keywords in AVAILABILITY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return status
    return "available"  # default: assumiamo disponibile


def _detect_contact(text: str) -> str | None:
    """Estrae la prima informazione di contatto trovata (DM, WhatsApp, telefono...)."""
    m = CONTACT_RE.search(text)
    if m:
        return m.group(0).strip()
    return None


def _is_watch_related(text: str) -> bool:
    text_lower = text.lower()
    return any(sig in text_lower for sig in WATCH_SIGNALS)


def _normalize_ocr_text(text: str) -> str:
    """
    Normalizza output OCR frequente:
    - Semicolone tra cifre → virgola  (11.500;00€ → 11.500,00€)
    - Rimuovi caratteri di controllo
    - Comprimi whitespace multiplo
    """
    # Semicolone tra cifre confuso con virgola
    text = re.sub(r'(\d);(\d)', r'\1,\2', text)
    # Pipe o barra verticale tra cifre → 1 (OCR confonde "1" e "|")
    text = re.sub(r'(\s)\|(\s)', r'\g<1>1\g<2>', text)
    # Rimuovi caratteri di controllo diversi da \n e \t
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    # Comprimi whitespace
    text = re.sub(r'\s{3,}', '\n', text)
    return text.strip()


# ── OCR ────────────────────────────────────────────────────────────────────────

def ocr_image(image_path: str) -> str:
    """
    Esegue OCR sull'immagine con pre-processing per testo su sfondi colorati.
    Tenta prima la combinazione ita+eng, fallback su eng.
    """
    try:
        import pytesseract
        from PIL import Image, ImageFilter, ImageEnhance, ImageOps

        img = Image.open(image_path)

        # Converti in RGB (rimuove trasparenza)
        img = img.convert("RGB")

        # Ridimensiona se troppo piccola (OCR peggiora sotto 300dpi)
        w, h = img.size
        if w < 800:
            scale = 800 / w
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        # Aumenta contrasto (fondamentale per testo su stories colorate)
        img = ImageEnhance.Contrast(img).enhance(2.2)
        # Aumenta nitidezza
        img = img.filter(ImageFilter.SHARPEN)

        # Prova prima lingua italiana+inglese
        try:
            text = pytesseract.image_to_string(
                img,
                lang="ita+eng",
                config="--psm 11 --oem 3",
            )
        except Exception:
            # Fallback se pack lingua ita non installato
            text = pytesseract.image_to_string(
                img,
                lang="eng",
                config="--psm 11 --oem 3",
            )

        return _normalize_ocr_text(text)

    except ImportError:
        logger.debug("pytesseract non installato — OCR disabilitato")
        return ""
    except Exception as e:
        logger.debug(f"OCR error {image_path}: {e}")
        return ""


# ── Funzione principale ────────────────────────────────────────────────────────

def parse_frame(
    screenshot_path: str,
    raw_page_text: str,
    username: str,
    timestamp: str,
    post_url: str = "",
) -> dict | None:
    """
    Processa un frame (screenshot + testo DOM) ed estrae dati strutturati.

    Pipeline:
      1. OCR dell'immagine
      2. Combina OCR + testo DOM
      3. Validazione orologio-related
      4. Estrazione prezzo (obbligatorio)
      5. Estrazione brand, referenza, condizione, disponibilità, contatto
      6. Calcolo confidence score

    Ritorna None se:
      - il frame non è orologio-related
      - non si riesce ad estrarre un prezzo
    """
    ocr_text = ocr_image(screenshot_path)
    combined = f"{ocr_text}\n{raw_page_text}"

    # Validazione: deve contenere segnali legati agli orologi
    if not _is_watch_related(combined) and not _is_watch_related(raw_page_text):
        return None

    # Prezzo: obbligatorio
    price = _parse_price(combined) or _parse_price(raw_page_text)
    if not price:
        return None

    # Valuta
    currency = _detect_currency(combined)

    # Brand e referenza
    brand = _detect_brand(combined)
    reference = _detect_reference(combined)

    # Condizione e disponibilità
    condition = _detect_condition(combined)
    availability = _detect_availability(combined)

    # Informazioni di contatto
    contact = _detect_contact(combined)

    # Full-set / documenti
    has_full_set = any(
        kw in combined.lower()
        for kw in CONDITION_KEYWORDS["full_set"]
    )
    has_no_papers = any(
        kw in combined.lower()
        for kw in CONDITION_KEYWORDS["no_papers"]
    )

    # ── Confidence score ──────────────────────────────────────────────────────
    # Ogni segnale affidabile aumenta il punteggio.
    confidence = 0.3  # base: trovato prezzo + segnale orologio
    if brand:
        confidence += 0.2
    if reference:
        confidence += 0.3
    if ocr_text:
        confidence += 0.1
    if condition != "unknown":
        confidence += 0.05
    if contact:
        confidence += 0.05
    confidence = round(min(1.0, confidence), 2)

    # Testo pulito (max 400 caratteri, senza spazi multipli)
    text_raw = " ".join(combined.split())[:400]

    return {
        "source": "instagram_story",
        "username": username,
        "price": price,
        "currency": currency,
        "brand": brand,
        "reference": reference,
        "condition": condition,
        "availability": availability,
        "has_full_set": has_full_set,
        "has_no_papers": has_no_papers,
        "contact": contact,
        "text_raw": text_raw,
        "image_path": screenshot_path,
        "post_url": post_url,
        "timestamp": timestamp,
        "confidence": confidence,
        "ocr_text": ocr_text[:600],
    }
