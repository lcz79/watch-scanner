"""
Validatore numeri seriali per orologi di lusso.
Le tabelle sono basate su documentazione storica nota per ciascun brand.
"""
import re
from dataclasses import dataclass, field
from utils.logger import get_logger

logger = get_logger("verification.serial")


@dataclass
class SerialValidationResult:
    is_valid_format: bool
    estimated_year: int | None
    year_range: tuple[int, int] | None  # (from, to) — None se non determinabile
    brand: str
    notes: str
    warnings: list[str] = field(default_factory=list)
    plausible: bool = True  # False se il seriale è chiaramente falso


# ---------------------------------------------------------------------------
# ROLEX
# ---------------------------------------------------------------------------
# Fonte: guide storiche comunità collezionisti, Rolex Explorer's Society
# I seriali Rolex vengono assegnati in batch, non in sequenza temporale lineare,
# quindi gli anni sono sempre range approssimativi.

_ROLEX_LETTER_TABLE: list[tuple[str, int, int]] = [
    # (prefix, year_from, year_to)
    ("R", 1987, 1988),
    ("L", 1988, 1989),
    ("E", 1990, 1991),
    ("X", 1991, 1992),
    ("N", 1993, 1993),
    ("C", 1994, 1994),
    ("S", 1994, 1995),
    ("W", 1995, 1996),
    ("T", 1996, 1997),
    ("U", 1997, 1998),
    ("A", 1998, 1999),
    ("P", 1999, 2000),
    ("K", 2000, 2001),
    ("Y", 2001, 2002),
    ("F", 2002, 2003),
    ("D", 2003, 2004),
    ("M", 2004, 2005),
    ("V", 2005, 2006),
    ("Z", 2006, 2007),
    ("G", 2007, 2008),
    # H, J, O, Q, B, I non usate convenzionalmente
]

_ROLEX_LETTER_MAP: dict[str, tuple[int, int]] = {
    row[0]: (row[1], row[2]) for row in _ROLEX_LETTER_TABLE
}


def validate_rolex_serial(serial: str) -> SerialValidationResult:
    """
    Valida un numero seriale Rolex.

    Schema storico:
    - < 100000          → pre-1926 (molto raro)
    - 100000–200000     → 1926–1953
    - 200000–999999     → 1954–1970
    - 1000000–1999999   → 1964–1985
    - 2000000–9999999   → 1975–1987
    - Lettera + 6 cifre → 1987–2010 (vedi tabella sopra)
    - 8 caratteri alfanumerici casuali (es. X5J23819) → 2010+
    """
    s = serial.strip().upper()
    warnings: list[str] = []

    # --- Pattern 2010+: 8 caratteri alfanumerici (mix lettere/numeri) ---
    if re.match(r"^[A-Z0-9]{8}$", s) and not s.isdigit():
        # Ulteriore check: almeno una lettera e un numero
        has_letter = any(c.isalpha() for c in s)
        has_digit = any(c.isdigit() for c in s)
        if has_letter and has_digit:
            return SerialValidationResult(
                is_valid_format=True,
                estimated_year=2015,
                year_range=(2010, None),
                brand="Rolex",
                notes="Formato post-2010: 8 caratteri alfanumerici casuali. Anno stimato 2010+.",
                plausible=True,
            )

    # --- Pattern lettera + 6 cifre (1987–2010) ---
    match_letter = re.match(r"^([A-Z])(\d{6})$", s)
    if match_letter:
        prefix = match_letter.group(1)
        if prefix in _ROLEX_LETTER_MAP:
            y_from, y_to = _ROLEX_LETTER_MAP[prefix]
            estimated = (y_from + y_to) // 2
            return SerialValidationResult(
                is_valid_format=True,
                estimated_year=estimated,
                year_range=(y_from, y_to),
                brand="Rolex",
                notes=f"Prefisso '{prefix}': produzione circa {y_from}–{y_to}.",
                plausible=True,
            )
        else:
            warnings.append(f"Prefisso lettera '{prefix}' non mappato nelle tabelle Rolex.")
            return SerialValidationResult(
                is_valid_format=False,
                estimated_year=None,
                year_range=None,
                brand="Rolex",
                notes=f"Lettera '{prefix}' non usata da Rolex nelle serie storiche.",
                warnings=warnings,
                plausible=False,
            )

    # --- Tutto numerico ---
    if not s.isdigit():
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Rolex",
            notes="Formato non valido: il seriale contiene caratteri non attesi.",
            warnings=["Seriale con caratteri non validi per Rolex"],
            plausible=False,
        )

    n = int(s)
    digits = len(s)

    if digits < 5:
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Rolex",
            notes="Seriale troppo corto (minimo 5 cifre per Rolex post-1920).",
            warnings=["Troppo poche cifre"],
            plausible=False,
        )

    if digits > 8:
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Rolex",
            notes="Seriale troppo lungo per il formato numerico Rolex.",
            warnings=["Troppo molte cifre"],
            plausible=False,
        )

    # Range numerici storici
    if n < 100_000:
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=1930,
            year_range=(1910, 1953),
            brand="Rolex",
            notes="Seriale very early (pre-1953), orologio da collezione.",
            plausible=True,
        )
    elif n < 200_000:
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=1940,
            year_range=(1926, 1953),
            brand="Rolex",
            notes="Seriale early (1926–1953).",
            plausible=True,
        )
    elif n < 1_000_000:
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=1962,
            year_range=(1954, 1970),
            brand="Rolex",
            notes="Seriale 6 cifre (1954–1970).",
            plausible=True,
        )
    elif n < 2_000_000:
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=1975,
            year_range=(1964, 1985),
            brand="Rolex",
            notes="Seriale 7 cifre inizio (1964–1985).",
            plausible=True,
        )
    elif n < 10_000_000:
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=1987,
            year_range=(1975, 1987),
            brand="Rolex",
            notes="Seriale 7 cifre (1975–1987).",
            plausible=True,
        )
    else:
        # 8 cifre tutte numeriche non è un formato standard moderno
        warnings.append("8 cifre tutte numeriche non corrisponde al formato post-2010 (che è alfanumerico).")
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Rolex",
            notes="Formato 8 cifre numeriche non valido per Rolex (post-2010 usa alfanumerico).",
            warnings=warnings,
            plausible=False,
        )


# ---------------------------------------------------------------------------
# OMEGA
# ---------------------------------------------------------------------------
# Fonte: Omega Museum, Omega Serial Number Database, Antiquorum catalogues
# I seriali Omega sono sequenziali e più lineari di Rolex.

_OMEGA_SERIAL_RANGES: list[tuple[int, int, int]] = [
    # (serial_from, serial_to, year)
    (1, 9999, 1884),
    (10000, 50000, 1892),
    (50001, 100000, 1896),
    (100001, 150000, 1900),
    (150001, 200000, 1903),
    (200001, 250000, 1905),
    (250001, 350000, 1907),
    (350001, 500000, 1910),
    (500001, 750000, 1913),
    (750001, 1000000, 1916),
    (1000001, 1500000, 1919),
    (1500001, 2000000, 1922),
    (2000001, 2500000, 1924),
    (2500001, 3000000, 1926),
    (3000001, 4000000, 1928),
    (4000001, 5000000, 1931),
    (5000001, 6000000, 1934),
    (6000001, 7000000, 1937),
    (7000001, 8000000, 1940),
    (8000001, 9000000, 1943),
    (9000001, 10000000, 1946),
    (10000001, 11000000, 1948),
    (11000001, 12500000, 1950),
    (12500001, 14000000, 1952),
    (14000001, 16000000, 1954),
    (16000001, 18000000, 1956),
    (18000001, 20000000, 1958),
    (20000001, 22000000, 1960),
    (22000001, 24000000, 1962),
    (24000001, 26000000, 1964),
    (26000001, 28000000, 1966),
    (28000001, 30000000, 1968),
    (30000001, 33000000, 1970),
    (33000001, 36000000, 1972),
    (36000001, 39000000, 1974),
    (39000001, 42000000, 1976),
    (42000001, 45000000, 1978),
    (45000001, 48000000, 1980),
    (48000001, 51000000, 1982),
    (51000001, 54000000, 1984),
    (54000001, 57000000, 1986),
    (57000001, 60000000, 1988),
    (60000001, 64000000, 1990),
    (64000001, 68000000, 1992),
    (68000001, 72000000, 1994),
    (72000001, 76000000, 1996),
    (76000001, 80000000, 1998),
    (80000001, 84000000, 2000),
    (84000001, 88000000, 2002),
    (88000001, 92000000, 2004),
    (92000001, 96000000, 2006),
    (96000001, 100000000, 2008),
]


def validate_omega_serial(serial: str) -> SerialValidationResult:
    """
    Valida un numero seriale Omega.
    Omega usa seriali numerici sequenziali dal 1884.
    Dal ~2010 usa un formato alfanumerico diverso.
    """
    s = serial.strip().upper()
    warnings: list[str] = []

    # --- Formato post-2009: tipicamente inizia con numero casuale o formato diverso ---
    # Omega post-2010 ha seriali di 8 cifre che continuano la sequenza sopra 100M
    # oppure usa formato card (non seriale classico visibile sul fondello)

    if not s.isdigit():
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Omega",
            notes="Seriale Omega non numerico: formato non riconosciuto.",
            warnings=["Seriale non numerico"],
            plausible=False,
        )

    n = int(s)
    digits = len(s)

    if digits < 4:
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Omega",
            notes="Seriale troppo corto per Omega.",
            warnings=["Troppo poche cifre"],
            plausible=False,
        )

    # Ricerca nelle tabelle storiche
    for serial_from, serial_to, year in _OMEGA_SERIAL_RANGES:
        if serial_from <= n <= serial_to:
            # Stima anno con interpolazione lineare
            frac = (n - serial_from) / max(1, serial_to - serial_from)
            next_year = year + 2  # ogni range è ~2 anni
            estimated = int(year + frac * (next_year - year))
            return SerialValidationResult(
                is_valid_format=True,
                estimated_year=estimated,
                year_range=(year, year + 2),
                brand="Omega",
                notes=f"Seriale Omega stimato anno circa {estimated} (range {year}–{year+2}).",
                plausible=True,
            )

    # Oltre 100M → post-2008
    if n > 100_000_000:
        est_year = 2008 + ((n - 100_000_000) // 4_000_000)
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=min(est_year, 2025),
            year_range=(2008, None),
            brand="Omega",
            notes=f"Seriale Omega post-2008, stimato circa {min(est_year, 2025)}.",
            plausible=True,
        )

    return SerialValidationResult(
        is_valid_format=False,
        estimated_year=None,
        year_range=None,
        brand="Omega",
        notes="Seriale non rientra nei range storici Omega documentati.",
        warnings=["Seriale fuori range"],
        plausible=False,
    )


# ---------------------------------------------------------------------------
# PATEK PHILIPPE
# ---------------------------------------------------------------------------
# Fonte: Patek Philippe Museum catalogs, Christie's auction archives
# Patek usa una numerazione interna meno pubblicizzata.

_PATEK_SERIAL_RANGES: list[tuple[int, int, int]] = [
    (1, 9999, 1839),
    (10000, 29999, 1868),
    (30000, 64999, 1878),
    (65000, 99999, 1885),
    (100000, 149999, 1893),
    (150000, 199999, 1898),
    (200000, 249999, 1903),
    (250000, 299999, 1907),
    (300000, 349999, 1910),
    (350000, 399999, 1914),
    (400000, 449999, 1917),
    (450000, 499999, 1920),
    (500000, 549999, 1923),
    (550000, 599999, 1926),
    (600000, 649999, 1929),
    (650000, 699999, 1932),
    (700000, 749999, 1935),
    (750000, 799999, 1938),
    (800000, 849999, 1941),
    (850000, 899999, 1944),
    (900000, 949999, 1948),
    (950000, 999999, 1951),
    (1000000, 1099999, 1953),
    (1100000, 1199999, 1956),
    (1200000, 1299999, 1959),
    (1300000, 1399999, 1962),
    (1400000, 1499999, 1965),
    (1500000, 1599999, 1968),
    (1600000, 1699999, 1971),
    (1700000, 1799999, 1974),
    (1800000, 1899999, 1977),
    (1900000, 1999999, 1980),
    (2000000, 2199999, 1983),
    (2200000, 2399999, 1986),
    (2400000, 2599999, 1989),
    (2600000, 2799999, 1992),
    (2800000, 2999999, 1995),
    (3000000, 3299999, 1997),
    (3300000, 3599999, 2000),
    (3600000, 3899999, 2003),
    (3900000, 4199999, 2006),
    (4200000, 4499999, 2009),
    (4500000, 4799999, 2012),
    (4800000, 5099999, 2015),
    (5100000, 5399999, 2018),
    (5400000, 5699999, 2021),
    (5700000, 5999999, 2024),
]


def validate_patek_serial(serial: str) -> SerialValidationResult:
    """
    Valida un numero seriale Patek Philippe.
    Patek usa seriali numerici dalla fondazione (1839).
    Il fondello riporta il seriale inciso a mano nei pezzi vintage.
    """
    s = serial.strip()
    warnings: list[str] = []

    if not s.isdigit():
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Patek Philippe",
            notes="Seriale Patek Philippe deve essere numerico.",
            warnings=["Seriale non numerico"],
            plausible=False,
        )

    n = int(s)

    if n < 1 or n > 6_000_000:
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Patek Philippe",
            notes="Seriale fuori dai range plausibili Patek Philippe (1–6.000.000).",
            warnings=["Numero seriale fuori range"],
            plausible=False,
        )

    for serial_from, serial_to, year in _PATEK_SERIAL_RANGES:
        if serial_from <= n <= serial_to:
            frac = (n - serial_from) / max(1, serial_to - serial_from)
            next_year = year + 3
            estimated = int(year + frac * (next_year - year))
            return SerialValidationResult(
                is_valid_format=True,
                estimated_year=estimated,
                year_range=(year, year + 3),
                brand="Patek Philippe",
                notes=f"Seriale Patek Philippe produzione stimata {estimated} (range {year}–{year+3}).",
                plausible=True,
            )

    return SerialValidationResult(
        is_valid_format=False,
        estimated_year=None,
        year_range=None,
        brand="Patek Philippe",
        notes="Seriale non corrisponde ai range storici Patek Philippe documentati.",
        warnings=["Range seriale non trovato"],
        plausible=False,
    )


# ---------------------------------------------------------------------------
# AUDEMARS PIGUET
# ---------------------------------------------------------------------------
# AP usa seriali numerici. La documentazione pubblica è limitata.

def validate_ap_serial(serial: str) -> SerialValidationResult:
    """
    Valida un numero seriale Audemars Piguet.
    AP usa seriali numerici sequenziali (documentazione pubblica limitata).
    Range noti approssimativi.
    """
    s = serial.strip()
    warnings = ["Nota: tabella seriali AP è meno documentata pubblicamente rispetto ad altri brand."]

    if not s.isdigit():
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Audemars Piguet",
            notes="Seriale AP deve essere numerico.",
            warnings=["Seriale non numerico"],
            plausible=False,
        )

    n = int(s)

    # Ranges AP approssimativi
    if n < 1000:
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=1880,
            year_range=(1875, 1920),
            brand="Audemars Piguet",
            notes="Seriale very early AP (fine 1800 - inizio 1900).",
            warnings=warnings,
            plausible=True,
        )
    elif n < 50000:
        year = 1875 + int((n / 50000) * 70)
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=year,
            year_range=(1875, 1945),
            brand="Audemars Piguet",
            notes=f"Seriale AP vintage, stimato circa {year}.",
            warnings=warnings,
            plausible=True,
        )
    elif n < 200000:
        year = 1945 + int(((n - 50000) / 150000) * 25)
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=year,
            year_range=(1945, 1970),
            brand="Audemars Piguet",
            notes=f"Seriale AP stimato circa {year}.",
            warnings=warnings,
            plausible=True,
        )
    elif n < 500000:
        year = 1970 + int(((n - 200000) / 300000) * 15)
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=year,
            year_range=(1970, 1985),
            brand="Audemars Piguet",
            notes=f"Seriale AP epoca Royal Oak, stimato circa {year}.",
            warnings=warnings,
            plausible=True,
        )
    elif n < 1000000:
        year = 1985 + int(((n - 500000) / 500000) * 10)
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=year,
            year_range=(1985, 1995),
            brand="Audemars Piguet",
            notes=f"Seriale AP stimato circa {year}.",
            warnings=warnings,
            plausible=True,
        )
    elif n < 2000000:
        year = 1995 + int(((n - 1000000) / 1000000) * 10)
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=year,
            year_range=(1995, 2005),
            brand="Audemars Piguet",
            notes=f"Seriale AP stimato circa {year}.",
            warnings=warnings,
            plausible=True,
        )
    elif n < 4000000:
        year = 2005 + int(((n - 2000000) / 2000000) * 10)
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=year,
            year_range=(2005, 2015),
            brand="Audemars Piguet",
            notes=f"Seriale AP stimato circa {year}.",
            warnings=warnings,
            plausible=True,
        )
    elif n < 8000000:
        year = 2015 + int(((n - 4000000) / 4000000) * 10)
        return SerialValidationResult(
            is_valid_format=True,
            estimated_year=min(year, 2026),
            year_range=(2015, None),
            brand="Audemars Piguet",
            notes=f"Seriale AP recente, stimato circa {min(year, 2026)}.",
            warnings=warnings,
            plausible=True,
        )
    else:
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand="Audemars Piguet",
            notes="Seriale AP fuori dai range documentati.",
            warnings=warnings + ["Numero troppo alto"],
            plausible=False,
        )


# ---------------------------------------------------------------------------
# TUDOR
# ---------------------------------------------------------------------------
# Tudor ha condiviso seriali con Rolex (stessa fabbrica) fino a un certo punto.
# Seriali Tudor vintage sono simili a Rolex. Modelli moderni usano formato diverso.

def validate_tudor_serial(serial: str) -> SerialValidationResult:
    """
    Valida un numero seriale Tudor.
    Tudor vintage condivideva il formato seriale con Rolex.
    Dal 2010 circa Tudor usa seriali propri.
    """
    s = serial.strip().upper()

    # Formato moderno Tudor (post-2010): alfanumerico tipo Rolex post-2010
    if re.match(r"^[A-Z0-9]{8}$", s) and not s.isdigit():
        has_letter = any(c.isalpha() for c in s)
        has_digit = any(c.isdigit() for c in s)
        if has_letter and has_digit:
            return SerialValidationResult(
                is_valid_format=True,
                estimated_year=2015,
                year_range=(2010, None),
                brand="Tudor",
                notes="Formato Tudor moderno (post-2010): 8 caratteri alfanumerici.",
                plausible=True,
            )

    # Tudor vintage usa lo stesso schema a lettere di Rolex (stessa madre — Rolex SA)
    match_letter = re.match(r"^([A-Z])(\d{6})$", s)
    if match_letter:
        prefix = match_letter.group(1)
        if prefix in _ROLEX_LETTER_MAP:
            y_from, y_to = _ROLEX_LETTER_MAP[prefix]
            estimated = (y_from + y_to) // 2
            return SerialValidationResult(
                is_valid_format=True,
                estimated_year=estimated,
                year_range=(y_from, y_to),
                brand="Tudor",
                notes=f"Seriale Tudor/Rolex condiviso, prefisso '{prefix}': circa {y_from}–{y_to}.",
                warnings=["Tudor vintage condivide il sistema seriale con Rolex"],
                plausible=True,
            )

    # Tutto numerico — stesse regole di Rolex vintage
    if s.isdigit():
        n = int(s)
        digits = len(s)

        if digits < 5:
            return SerialValidationResult(
                is_valid_format=False,
                estimated_year=None,
                year_range=None,
                brand="Tudor",
                notes="Seriale Tudor troppo corto.",
                warnings=["Troppo poche cifre"],
                plausible=False,
            )

        if n < 1_000_000:
            return SerialValidationResult(
                is_valid_format=True,
                estimated_year=1965,
                year_range=(1940, 1970),
                brand="Tudor",
                notes="Seriale Tudor vintage (ante 1970).",
                plausible=True,
            )
        elif n < 10_000_000:
            return SerialValidationResult(
                is_valid_format=True,
                estimated_year=1985,
                year_range=(1970, 2000),
                brand="Tudor",
                notes="Seriale Tudor (1970–2000).",
                plausible=True,
            )

    return SerialValidationResult(
        is_valid_format=False,
        estimated_year=None,
        year_range=None,
        brand="Tudor",
        notes="Formato seriale Tudor non riconosciuto.",
        warnings=["Formato non corrispondente ai pattern Tudor documentati"],
        plausible=False,
    )


# ---------------------------------------------------------------------------
# ROUTER PRINCIPALE
# ---------------------------------------------------------------------------

_BRAND_VALIDATORS = {
    "rolex": validate_rolex_serial,
    "patek philippe": validate_patek_serial,
    "patek": validate_patek_serial,
    "omega": validate_omega_serial,
    "audemars piguet": validate_ap_serial,
    "ap": validate_ap_serial,
    "tudor": validate_tudor_serial,
}


def validate_serial(brand: str, serial: str) -> SerialValidationResult:
    """
    Router principale: chiama il validator giusto per il brand.
    Se il brand non è supportato, restituisce un risultato con nota.
    """
    if not serial or not serial.strip():
        return SerialValidationResult(
            is_valid_format=False,
            estimated_year=None,
            year_range=None,
            brand=brand,
            notes="Numero seriale non fornito.",
            warnings=["Seriale vuoto"],
            plausible=False,
        )

    validator = _BRAND_VALIDATORS.get(brand.lower().strip())
    if validator:
        try:
            return validator(serial)
        except Exception as e:
            logger.warning(f"Errore validazione seriale {brand} '{serial}': {e}")
            return SerialValidationResult(
                is_valid_format=False,
                estimated_year=None,
                year_range=None,
                brand=brand,
                notes=f"Errore durante la validazione: {e}",
                warnings=["Errore interno validazione"],
                plausible=False,
            )
    else:
        return SerialValidationResult(
            is_valid_format=True,  # non possiamo confutarlo
            estimated_year=None,
            year_range=None,
            brand=brand,
            notes=f"Brand '{brand}' non ha un validator seriale specifico. Verifica manuale raccomandata.",
            warnings=[f"Nessun validator disponibile per {brand}"],
            plausible=True,
        )
