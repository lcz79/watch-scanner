"""
Mock data per sviluppo senza API key.
Ogni listing simula un annuncio INDIVIDUALE (come un vero scraper restituirebbe):
- URL diretto all'annuncio specifico
- Prezzo dell'annuncio
- Nome del venditore
- Condizione
- Data di pubblicazione

In produzione (MOCK_MODE=false) questi dati vengono sostituiti
da listing reali scraped da Chrono24, eBay, Instagram, ecc.
"""

import random
import hashlib
from datetime import datetime, timedelta
from models.schemas import WatchListing

# Prezzi di mercato reali per referenza (EUR, aprile 2026)
REFERENCE_BASE_PRICES: dict[str, float] = {
    # Rolex Submariner
    "116610LN": 13500,
    "116610LV": 16800,   # Hulk
    "126610LN": 14200,
    "126610LV": 17500,
    "126710BLNR": 17200, # Batman
    "116613LB": 16100,
    # Rolex Daytona
    "116500LN": 36000,
    "116520":   18000,
    # Rolex Datejust
    "126334":   11800,
    "126300":    9900,
    # Rolex Day-Date
    "228235":   38000,
    # Patek Philippe
    "5711/1A":  148000,
    "5726A":     88000,
    "5167A":     57000,
    # Audemars Piguet
    "15500ST":   34000,
    "26240CE":   47000,
    "DEFAULT":    8000,
}

CONDITIONS_WEIGHTED = ["mint"] * 3 + ["good"] * 4 + ["fair"] * 2 + ["new"] * 1
EXTRAS = ["Scatola e garanzia", "Full set", "Solo orologio", "Con carte d'origine", "Box & Papers"]

# Reseller Instagram reali che vendono orologi (account pubblici noti)
INSTAGRAM_RESELLERS = [
    ("watchesofitalia",    "Milano"),
    ("luxurywatchesmilan", "Milano"),
    ("watchhunter_eu",     "Amsterdam"),
    ("preloved_watches_ch","Zurigo"),
    ("chronosreseller",    "Roma"),
    ("orologi_secondmano", "Torino"),
    ("watchmarket_it",     "Firenze"),
    ("genevawatch_resell", "Ginevra"),
]

CHRONO24_SELLERS = [
    ("WatchBox Italia",        "Milano",   4.9),
    ("Chrono Hunter GmbH",     "Zurigo",   4.8),
    ("Premier Watches Ltd",    "Londra",   4.7),
    ("Europa Star Watches",    "Ginevra",  4.9),
    ("OrologiPreziosi SRL",    "Roma",     4.6),
    ("Nordic Watches AB",      "Stoccolma",4.8),
    ("Watch Avenue SA",        "Ginevra",  4.7),
    ("Tempus Fugit GmbH",      "Monaco",   4.9),
    ("Xupes Limited",          "Londra",   4.8),
    ("Wrist Aficionado",       "New York", 4.7),
]

EBAY_SELLERS = [
    ("watchmania2023",    "Milano"),
    ("orologi_top",       "Roma"),
    ("swiss_time_it",     "Zurigo"),
    ("luxtimepieces",     "Milano"),
    ("watchreseller_eu",  "Parigi"),
    ("premium_watches_de","Monaco"),
]


def _base_price(reference: str) -> float:
    return REFERENCE_BASE_PRICES.get(reference.upper(), REFERENCE_BASE_PRICES["DEFAULT"])


def _rng(seed_str: str) -> random.Random:
    """RNG deterministico: stessa referenza = stessi mock ad ogni chiamata."""
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    return random.Random(seed)


def _fake_chrono24_id() -> str:
    return str(random.randint(10000000, 99999999))

def _fake_ebay_id() -> str:
    return str(random.randint(100000000000, 999999999999))

def _fake_ig_code() -> str:
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    return "".join(random.choices(chars, k=11))


def mock_chrono24_listings(reference: str) -> list[WatchListing]:
    base = _base_price(reference)
    rng = _rng(reference + "chrono24")
    count = rng.randint(4, 8)
    listings = []
    ref_encoded = reference.replace("/", "-").replace(" ", "+")
    search_url = f"https://www.chrono24.it/search/index.htm?query={ref_encoded}&dosearch=1&resultview=list"
    for i in range(count):
        seller, location, rating = rng.choice(CHRONO24_SELLERS)
        price = round(base * rng.uniform(0.91, 1.12) / 10) * 10
        days_ago = rng.randint(0, 30)
        condition = rng.choice(CONDITIONS_WEIGHTED)
        extra = rng.choice(EXTRAS)
        listings.append(WatchListing(
            source="chrono24",
            reference=reference,
            price=price,
            currency="EUR",
            seller=seller,
            url=search_url,
            condition=condition,
            scraped_at=datetime.now() - timedelta(days=days_ago),
            location=location,
            description=f"{reference} · {condition.capitalize()} · {extra} · ⭐ {rating}",
        ))
    return listings


def mock_ebay_listings(reference: str) -> list[WatchListing]:
    base = _base_price(reference)
    rng = _rng(reference + "ebay")
    count = rng.randint(3, 6)
    listings = []
    ref_encoded = reference.replace("/", "-").replace(" ", "+")
    search_url = f"https://www.ebay.it/sch/31387/i.html?_nkw={ref_encoded}&_sop=15&LH_BIN=1"
    for _ in range(count):
        seller, location = rng.choice(EBAY_SELLERS)
        price = round(base * rng.uniform(0.88, 1.08) / 10) * 10
        days_ago = rng.randint(0, 14)
        condition = rng.choice(CONDITIONS_WEIGHTED)
        listings.append(WatchListing(
            source="ebay",
            reference=reference,
            price=price,
            currency="EUR",
            seller=seller,
            url=search_url,
            condition=condition,
            scraped_at=datetime.now() - timedelta(days=days_ago),
            location=location,
            description=f"{reference} {condition} — Spedizione inclusa",
        ))
    return listings


def mock_watchbox_listings(reference: str) -> list[WatchListing]:
    base = _base_price(reference)
    rng = _rng(reference + "watchbox")
    count = rng.randint(2, 4)
    listings = []
    ref_encoded = reference.replace("/", "-").replace(" ", "+")
    search_url = f"https://www.watchbox.com/search?q={ref_encoded}"
    for _ in range(count):
        price = round(base * rng.uniform(0.93, 1.10) / 10) * 10
        condition = rng.choice(["mint", "good", "mint"])
        listings.append(WatchListing(
            source="watchbox",
            reference=reference,
            price=price,
            currency="EUR",
            seller="WatchBox",
            url=search_url,
            condition=condition,
            scraped_at=datetime.now() - timedelta(days=rng.randint(0, 20)),
            location="Philadelphia, USA",
            description=f"{reference} · {condition.capitalize()} · Certificato WatchBox",
        ))
    return listings


def mock_watchfinder_listings(reference: str) -> list[WatchListing]:
    base = _base_price(reference)
    rng = _rng(reference + "watchfinder")
    count = rng.randint(2, 5)
    listings = []
    ref_encoded = reference.replace("/", "-").replace(" ", "+")
    search_url = f"https://www.watchfinder.co.uk/preowned-watches/list?q={ref_encoded}"
    for _ in range(count):
        price = round(base * rng.uniform(0.95, 1.15) / 10) * 10
        condition = rng.choice(["mint", "good"])
        listings.append(WatchListing(
            source="watchfinder",
            reference=reference,
            price=price,
            currency="EUR",
            seller="Watchfinder & Co.",
            url=search_url,
            condition=condition,
            scraped_at=datetime.now() - timedelta(days=rng.randint(0, 25)),
            location="Londra, UK",
            description=f"{reference} · {condition.capitalize()} · Garanzia 12 mesi",
        ))
    return listings


def mock_instagram_listings(reference: str) -> list[WatchListing]:
    """
    Simula annunci individuali di reseller Instagram.
    In produzione: ogni riga è un post/story reale con prezzo nella caption.
    """
    base = _base_price(reference)
    rng = _rng(reference + "instagram")
    count = rng.randint(3, 6)
    listings = []
    for _ in range(count):
        account, location = rng.choice(INSTAGRAM_RESELLERS)
        price = round(base * rng.uniform(0.86, 1.02) / 10) * 10
        post_code = _fake_ig_code()
        condition = rng.choice(["mint", "good", "unknown"])
        hours_ago = rng.randint(1, 96)
        listings.append(WatchListing(
            source="instagram",
            reference=reference,
            price=price,
            currency="EUR",
            seller=f"@{account}",
            url=f"https://www.instagram.com/{account}/",
            condition=condition,
            scraped_at=datetime.now() - timedelta(hours=hours_ago),
            location=location,
            image_url=f"https://picsum.photos/seed/{post_code}/400/400",
            description=f"Post di @{account} · {reference} · {condition.capitalize()} · DM per info",
        ))
    return listings


FACEBOOK_MARKETPLACE_SELLERS = [
    ("Marco R.",         "Milano"),
    ("Orologi Luxury",   "Roma"),
    ("WatchItaly",       "Firenze"),
    ("Swiss Time IT",    "Zurigo"),
    ("Chrono Deals",     "Torino"),
    ("LuxWatch Europe",  "Monaco"),
    ("Preloved Watches", "Amsterdam"),
    ("Milano Orologi",   "Milano"),
]

TIKTOK_WATCH_ACCOUNTS = [
    ("watchdealer_it",       "Milano"),
    ("orologi_lusso_ita",    "Roma"),
    ("rolex_reseller_eu",    "Zurigo"),
    ("watch_hunter_europe",  "Amsterdam"),
    ("luxury_time_italy",    "Firenze"),
    ("swiss_watch_deals",    "Ginevra"),
]


def mock_facebook_listings(reference: str) -> list[WatchListing]:
    """
    Simula annunci di Facebook Marketplace.
    In produzione: ogni riga è un annuncio Marketplace reale con prezzo.
    """
    base = _base_price(reference)
    rng = _rng(reference + "facebook")
    count = rng.randint(2, 5)
    listings = []
    for _ in range(count):
        seller, location = rng.choice(FACEBOOK_MARKETPLACE_SELLERS)
        # Facebook Marketplace: tipicamente privati, prezzi leggermente più bassi
        price = round(base * rng.uniform(0.83, 1.05) / 10) * 10
        item_id = rng.randint(1000000000, 9999999999)
        hours_ago = rng.randint(1, 72)
        condition = rng.choice(CONDITIONS_WEIGHTED)
        extra = rng.choice(EXTRAS)
        ref_encoded = reference.replace("/", "-").replace(" ", "+")
        listings.append(WatchListing(
            source="facebook_marketplace",
            reference=reference,
            price=price,
            currency="EUR",
            seller=seller,
            url=f"https://www.facebook.com/marketplace/search/?query={ref_encoded}&category_id=31387",
            condition=condition,
            scraped_at=datetime.now() - timedelta(hours=hours_ago),
            location=location,
            description=f"{reference} · {condition.capitalize()} · {extra} · Facebook Marketplace",
        ))
    return listings


def mock_tiktok_listings(reference: str) -> list[WatchListing]:
    """
    Simula video TikTok di reseller con prezzi in caption.
    In produzione: caption del video analizzata per referenza e prezzo.
    """
    base = _base_price(reference)
    rng = _rng(reference + "tiktok")
    count = rng.randint(1, 4)
    listings = []
    for _ in range(count):
        account, location = rng.choice(TIKTOK_WATCH_ACCOUNTS)
        # TikTok spesso prezzi competitivi (venditori giovani, meno intermediari)
        price = round(base * rng.uniform(0.84, 1.01) / 10) * 10
        video_id = rng.randint(7000000000000000000, 7999999999999999999)
        hours_ago = rng.randint(1, 48)
        condition = rng.choice(["mint", "good", "unknown"])
        listings.append(WatchListing(
            source="tiktok",
            reference=reference,
            price=price,
            currency="EUR",
            seller=f"@{account}",
            url=f"https://www.tiktok.com/@{account}",
            condition=condition,
            scraped_at=datetime.now() - timedelta(hours=hours_ago),
            location=location,
            description=f"Video TikTok · @{account} · {reference} · Prezzo: {price}€ · DM per info",
        ))
    return listings


def mock_vision_listings(reference: str) -> list[WatchListing]:
    """
    Vision AI: post social senza prezzo nella caption,
    ma il prezzo è stato estratto dall'immagine della stories.
    """
    base = _base_price(reference)
    rng = _rng(reference + "vision")
    count = rng.randint(1, 3)
    listings = []
    for _ in range(count):
        account, location = rng.choice(INSTAGRAM_RESELLERS)
        # Vision trova spesso le offerte migliori (non indicizzate)
        price = round(base * rng.uniform(0.84, 0.97) / 10) * 10
        post_code = _fake_ig_code()
        hours_ago = rng.randint(1, 36)
        listings.append(WatchListing(
            source="vision_ai",
            reference=reference,
            price=price,
            currency="EUR",
            seller=f"@{account}",
            url=f"https://www.instagram.com/{account}/",
            condition="unknown",
            scraped_at=datetime.now() - timedelta(hours=hours_ago),
            location=location,
            image_url=f"https://picsum.photos/seed/vision{post_code}/400/400",
            description=f"Prezzo estratto da stories di @{account} via GPT-4o Vision · {reference}",
        ))
    return listings
