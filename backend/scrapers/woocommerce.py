"""
Scraper per siti WooCommerce di dealer di orologi.
Usa l'API store pubblica /wp-json/wc/store/products — nessuna auth necessaria.
"""
import re
import httpx
from datetime import datetime
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing

logger = get_logger("scraper.woocommerce")


def _token_in_title(token: str, title_up: str) -> bool:
    """Controlla se un token è nel titolo. Per token alfabetici >= 7 chars usa prefix matching."""
    if token in title_up:
        return True
    if not token.isdigit() and len(token) >= 7:
        prefix = token[:max(5, len(token) - 2)]
        return prefix in title_up
    return False


def _parse_woo_price(price_html: str) -> float | None:
    """Parsa prezzi WooCommerce: rimuove HTML, estrae numero."""
    # WooCommerce manda il prezzo come HTML: "<span>12.500,00</span>"
    clean = re.sub(r'<[^>]+>', '', price_html).strip()
    clean = clean.replace('€', '').replace('EUR', '').replace('\xa0', '').strip()
    clean = clean.replace('.', '').replace(',', '.')
    try:
        p = float(clean)
        return p if p > 100 else None
    except Exception:
        return None


async def scrape_woocommerce(domain: str, reference: str) -> list[WatchListing]:
    """
    Scrapa prodotti WooCommerce via Store API.
    Tenta /wp-json/wc/store/products poi /wp-json/wc/store/v1/products come fallback.
    """
    base_url = f"https://{domain}" if not domain.startswith("http") else domain
    listings = []

    endpoints = [
        f"{base_url}/wp-json/wc/store/products",
        f"{base_url}/wp-json/wc/store/v1/products",
    ]

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for endpoint in endpoints:
            try:
                params = {"search": reference, "per_page": 30, "status": "publish"}
                r = await client.get(
                    endpoint,
                    params=params,
                    headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
                )

                if r.status_code != 200:
                    continue

                products = r.json()
                if not isinstance(products, list):
                    continue

                for prod in products:
                    name = prod.get("name", "")

                    # Filtra per reference: ogni token deve essere nel titolo
                    # Per token alfabetici usa prefix matching (tollera errori di battitura)
                    name_up = name.upper()
                    tokens = [t for t in reference.upper().split() if len(t) >= 3]
                    if tokens and not all(_token_in_title(t, name_up) for t in tokens):
                        continue

                    prices_obj = prod.get("prices", {})

                    # currency_minor_unit: WooCommerce Store API manda in centesimi
                    minor_unit = int(prices_obj.get("currency_minor_unit", 2))
                    divisor = 10 ** minor_unit  # di solito 100

                    price_raw = prices_obj.get("price", "") or prod.get("price", "")
                    price = _parse_woo_price(str(price_raw))
                    if price and price > 50000:  # probabilmente in centesimi
                        price = price / divisor
                    if not price:
                        price_range = prices_obj.get("price_range") or {}
                        price = _parse_woo_price(str(price_range.get("min_amount", "")))
                        if price and price > 50000:
                            price = price / divisor

                    if not price or not is_watch_listing(name, "", price):
                        continue

                    url = prod.get("permalink", base_url)

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
                        description=name,
                        image_url=image_url,
                    ))

                if listings:
                    break  # primo endpoint funzionante → stop

            except Exception as e:
                logger.debug(f"WooCommerce {domain} {endpoint}: {e}")
                continue

    logger.info(f"WooCommerce {domain}: {len(listings)} listing per {reference}")
    return listings


async def is_woocommerce(domain: str) -> bool:
    """Verifica se il sito usa WooCommerce."""
    base_url = f"https://{domain}" if not domain.startswith("http") else domain
    async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
        for endpoint in ["/wp-json/wc/store/products", "/wp-json/wc/store/v1/products"]:
            try:
                r = await client.get(
                    f"{base_url}{endpoint}?per_page=1",
                    headers={"Accept": "application/json"},
                )
                if r.status_code == 200 and isinstance(r.json(), list):
                    return True
            except Exception:
                pass
    return False
