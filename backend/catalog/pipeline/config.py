"""
Configurazione pipeline scraping referenze orologi.
Source primaria: WatchBase (watchbase.com) — database pubblico con
gerarchia brand → collection → reference.
"""

# Brand target con slug watchbase corrispondente
BRANDS = [
    ("Rolex",               "rolex"),
    ("Omega",               "omega"),
    ("Patek Philippe",      "patek-philippe"),
    ("Audemars Piguet",     "audemars-piguet"),
    ("Vacheron Constantin", "vacheron-constantin"),
    ("TAG Heuer",           "tag-heuer"),
    ("Tudor",               "tudor"),
    ("IWC",                 "iwc"),
    ("Breitling",           "breitling"),
    ("Panerai",             "panerai"),
    ("Cartier",             "cartier"),
    ("Jaeger-LeCoultre",    "jaeger-lecoultre"),
    ("A. Lange & Söhne",    "a-lange-sohne"),
    ("Richard Mille",       "richard-mille"),
    ("Hublot",              "hublot"),
    ("Zenith",              "zenith"),
    ("Longines",            "longines"),
    ("Seiko",               "seiko"),
    ("Grand Seiko",         "grand-seiko"),
    ("Nomos",               "nomos"),
    ("Glashütte Original",  "glashutte-original"),
    ("F.P. Journe",         "f-p-journe"),
    ("H. Moser & Cie",      "h-moser-cie"),
    ("MB&F",                "mb-f"),
    ("Urwerk",              "urwerk"),
]

BASE_URL = "https://watchbase.com"

# Rate limit tra richieste (secondi)
DELAY_BETWEEN_REQUESTS = 2.0
DELAY_BETWEEN_BRANDS   = 45.0

# File di output
OUTPUT_JSON = "../watches_full.json"   # relativo a pipeline/
CACHE_DIR   = ".cache"                 # cache HTML per non ri-scrapare

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xhtml;q=0.9,*/*;q=0.8",
}
