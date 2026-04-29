"""
Scraper per siti Shopify di dealer di orologi.
Usa l'API pubblica /products.json — nessun Playwright necessario.
"""
import httpx
from datetime import datetime
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing

logger = get_logger("scraper.shopify")

WATCH_BRANDS = [
    "rolex", "patek", "audemars", "omega", "tudor", "breitling",
    "iwc", "cartier", "hublot", "panerai", "richard mille", "vacheron",
    "jaeger", "zenith", "tag heuer", "longines", "blancpain",
]


def _token_in_title(token: str, title_up: str) -> bool:
    """Controlla se un token è nel titolo. Per token alfabetici >= 7 chars usa prefix matching
    (tollera varianti di battitura come 'Patrizzi' vs 'Patrizi')."""
    if token in title_up:
        return True
    # Per token alfabetici lunghi: cerca i primi max(5, len-2) caratteri (gestisce 1-2 errori)
    if not token.isdigit() and len(token) >= 7:
        prefix = token[:max(5, len(token) - 2)]
        return prefix in title_up
    return False


def _parse_price(price_str: str) -> float | None:
    """Parsa prezzi Shopify: '12500.00' → 12500.0"""
    try:
        p = float(str(price_str).replace(',', '.'))
        # Se è in centesimi (> 100000 e senza virgola), dividi per 100
        return p if p > 100 else None
    except Exception:
        return None


async def scrape_shopify(domain: str, reference: str) -> list[WatchListing]:
    """
    Scrapa tutti i prodotti di un negozio Shopify via /products.json.
    Filtra per reference e brand orologi.
    domain: es. "watchdealer.com" (senza https://)
    """
    base_url = f"https://{domain}" if not domain.startswith("http") else domain
    listings = []

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        page = 1
        while page <= 3:  # max 3 pagine da 250 prodotti = 750 prodotti
            try:
                r = await client.get(
                    f"{base_url}/products.json",
                    params={"limit": 250, "page": page},
                    headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
                )
                if r.status_code != 200:
                    break
                data = r.json()
                products = data.get("products", [])
                if not products:
                    break

                for prod in products:
                    from html import unescape
                    title = unescape(prod.get("title", ""))
                    title_lower = title.lower()

                    # Filtra per brand orologio
                    if not any(brand in title_lower for brand in WATCH_BRANDS):
                        continue

                    # Filtra per reference: ogni token deve essere nel titolo
                    # Per token alfabetici usa prefix matching (tollera errori di battitura)
                    title_up = title.upper()
                    tokens = [t for t in reference.upper().split() if len(t) >= 3]
                    if tokens and not all(_token_in_title(t, title_up) for t in tokens):
                        continue

                    # Prezzo dal primo variant disponibile
                    variants = prod.get("variants", [])
                    price = None
                    for variant in variants:
                        p = _parse_price(variant.get("price", 0))
                        if p and p > 100:
                            price = p
                            break

                    # Filtra prezzi placeholder (1€, 0€ = sold/hidden)
                    if not price or price < 100 or not is_watch_listing(title, "", price):
                        continue

                    # URL prodotto
                    handle = prod.get("handle", "")
                    url = f"{base_url}/products/{handle}" if handle else base_url

                    # Immagine
                    images = prod.get("images", [])
                    image_url = images[0].get("src") if images else None

                    listings.append(WatchListing(
                        source="reseller_website",
                        reference=reference,
                        price=price,
                        currency="EUR",
                        seller=domain,
                        url=url,
                        condition="unknown",
                        scraped_at=datetime.now(),
                        description=title,
                        image_url=image_url,
                    ))

                if len(products) < 250:
                    break  # ultima pagina
                page += 1

            except Exception as e:
                logger.debug(f"Shopify {domain} page {page}: {e}")
                break

    logger.info(f"Shopify {domain}: {len(listings)} listing per {reference}")
    return listings


async def is_shopify(domain: str) -> bool:
    """Verifica velocemente se un dominio usa Shopify."""
    base_url = f"https://{domain}" if not domain.startswith("http") else domain
    async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
        try:
            r = await client.get(
                f"{base_url}/products.json?limit=1",
                headers={"Accept": "application/json"},
            )
            if r.status_code == 200:
                data = r.json()
                return "products" in data
        except Exception:
            pass
    return False
