"""
Filtro per distinguere annunci di orologi completi da parti/accessori.

Logica:
- Parte da score 5 (neutro)
- Brand/modelli noti → +3
- Keyword orologio → +2
- Prezzo alto (>5000€) → +4, (>2000) → +2
- Prezzo basso (<MIN_WATCH_PRICE) → reject immediato
- EXCLUDE_KEYWORDS chiara → reject immediato
- PARTS_KEYWORD chiara → -4 ciascuna
- Parts + no brand/modello → reject immediato
- Soglia: score >= 5
"""

import re

# Soglia minima prezzo: sotto questa soglia l'annuncio è quasi certamente
# un accessorio, parte o prodotto non-orologio.
MIN_WATCH_PRICE: float = 300.0

# Parole che identificano INEQUIVOCABILMENTE un accessorio/parte — reject diretto
EXCLUDE_KEYWORDS = [
    # Cinturini e bracciali (senza orologio)
    "cinturino", "strap", "bracelet", "bracciale",
    "jubilee band", "oyster band",
    "clasp", "fibbia", "buckle",
    "deployant",
    # Scatole e documenti senza orologio
    "box only", "solo scatola", "empty box", "scatola vuota", "cofanetto vuoto",
    "papers only", "solo garanzia",
    "booklet", "libretto", "manuale d'uso",
    # Parti individuali
    "vetro", "crystal", "glass replacement",
    "corona", "crown only",
    "fondello", "case back", "caseback",
    "quadrante solo", "dial only", "solo quadrante",
    "lancette", "hands only",
    "bezel insert", "ghiera sola", "lunetta sola",
    "spring bar", "barrette",
    "end link",
    "pusher", "pushers",
    # Materiale pubblicitario / collezionismo non-orologio
    "libro", "book only", "poster", "catalogo", "catalogue", "brochure",
    # Ricambi / movimenti soli
    "ricambio", "spare part", "replacement part",
    "movement only", "solo movimento",
    "polishing cloth", "cleaning cloth",
    "loupe", "lupe",
]

# Accessori e ricambi CERTI — usati per scoring (non per reject immediato)
PARTS_KEYWORDS = [
    "cinturino", "strap", "bracelet", "deployant",
    "bezel", "lunetta", "ghiera",
    "caseback", "fondello",
    "dial", "quadrante",
    "lancette", "hands",
    "crown", "winding crown",
    "pusher", "pushers",
    "spring bar", "barrette",
    "end link",
    "scatola vuota", "empty box", "box only", "solo scatola", "cofanetto vuoto",
    "libretto", "booklet", "papers only", "solo garanzia", "manuale d'uso",
    "spare part", "ricambio", "replacement part",
    "loupe", "lupe",
    "polishing cloth", "cleaning cloth",
    "catalogo", "catalogue", "brochure",
]

# Brand di lusso noti → forte segnale orologio
BRAND_KEYWORDS = [
    "rolex", "omega", "patek", "philippe", "audemars", "piguet",
    "breitling", "tudor", "iwc", "cartier", "hublot",
    "richard mille", "vacheron", "constantin", "jaeger", "lecoultre", "lange",
    "panerai", "zenith", "tag heuer", "longines", "tissot",
    "seiko", "grand seiko", "blancpain", "chopard",
    "bvlgari", "bulgari", "montblanc", "piaget",
    "a. lange", "lange & söhne",
]

# Modelli noti → segnale orologio
MODEL_KEYWORDS = [
    "submariner", "daytona", "gmt", "datejust", "day-date", "explorer",
    "speedmaster", "seamaster", "constellation", "de ville",
    "nautilus", "aquanaut", "calatrava",
    "royal oak", "offshore",
    "navitimer", "superocean", "chronomat",
    "black bay", "pelagos",
    "portofino", "portugieser", "pilot",
    "santos", "tank", "ballon bleu",
    "luminor", "radiomir",
    "el primero",
    "aqua terra", "planet ocean",
]

# Keyword generiche orologio — includi se almeno una presente
WATCH_KEYWORDS = [
    "orologio", "watch", "timepiece", "segnatempo", "montre", "uhr",
    "cronografo", "chronograph",
    "automatico", "automatic", "mechanical",
    "full set", "con scatola", "con garanzia", "scatola e garanzia",
    "completo",
]

# Regex reference: cattura sia "116610LN" (solo cifre+lettere) sia "PAM00441"
# Pattern: almeno 4 cifre consecutive, con eventuale suffisso lettere
_REFERENCE_RE = re.compile(
    r'\b('
    r'[A-Z]{1,4}[\s\-]?\d{3,6}[A-Z0-9]{0,6}'   # PAM00441, IW3777
    r'|'
    r'\d{4,6}[A-Z]{0,4}\d{0,3}'                   # 116610LN, 5711/1A → 57111A
    r')\b',
    re.IGNORECASE
)


def _whole_word_match(keyword: str, text: str) -> bool:
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def _has_exclude_keyword(text_lower: str) -> bool:
    """Controlla se il testo contiene una parola di esclusione diretta."""
    for kw in EXCLUDE_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def is_watch_listing(title: str, description: str = "", price: float = 0) -> bool:
    """
    Determina se un annuncio è un orologio completo (non un accessorio/parte).

    Args:
        title: Titolo dell'annuncio
        description: Descrizione (opzionale)
        price: Prezzo in EUR (0 = ignora la soglia)

    Returns:
        True se l'annuncio è probabilmente un orologio completo.
    """
    text = (title + " " + description).strip()
    text_lower = text.lower()

    # --- Reject immediato: prezzo troppo basso ---
    if price > 0 and price < MIN_WATCH_PRICE:
        return False

    # --- Reject immediato: keyword esclusione esplicita ---
    if _has_exclude_keyword(text_lower):
        return False

    score = 5

    # --- Penalità PARTS_KEYWORDS ---
    found_parts = [kw for kw in PARTS_KEYWORDS if _whole_word_match(kw, text)]
    score -= 4 * len(found_parts)

    # --- Brand/modello → forte segnale positivo ---
    has_brand = any(kw in text_lower for kw in BRAND_KEYWORDS)
    has_model = any(kw in text_lower for kw in MODEL_KEYWORDS)
    if has_brand:
        score += 3
    if has_model:
        score += 2

    # --- Keyword orologio generico ---
    for kw in WATCH_KEYWORDS:
        if _whole_word_match(kw, text):
            score += 2

    # --- Reference number rilevata ---
    has_reference = bool(_REFERENCE_RE.search(text))
    if has_reference:
        score += 1

    # --- Reject immediato: parts_keyword + no brand + no modello ---
    if found_parts and not has_brand and not has_model:
        return False

    # --- Prezzo ---
    if price > 0:
        if price < 800:
            score -= 4
        elif price < 1500:
            score -= 2
        elif price > 10000:
            score += 4
        elif price > 5000:
            score += 3
        elif price > 2000:
            score += 2

    score = max(0, min(15, score))
    return score >= 5


def filter_watch_listings(listings: list, min_price: float = MIN_WATCH_PRICE) -> list:
    """
    Filtra una lista di WatchListing, tenendo solo gli orologi completi.

    Args:
        listings: Lista di WatchListing
        min_price: Soglia minima prezzo (default MIN_WATCH_PRICE)

    Returns:
        Lista filtrata di soli annunci orologio.
    """
    return [
        listing for listing in listings
        if is_watch_listing(
            listing.description or listing.seller or "",
            "",
            listing.price,
        )
        and (min_price <= 0 or listing.price >= min_price)
    ]
