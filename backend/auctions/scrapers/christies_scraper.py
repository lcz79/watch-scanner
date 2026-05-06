"""
Christie's Watches scraper.
Sito: https://www.christies.com/departments/watches-52-1.aspx
API JSON: https://www.christies.com/api/discoverywebsite/...

Christie's espone un'API JSON per la ricerca che possiamo interrogare.
"""
import asyncio
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.christies.com"
SEARCH_API = f"{BASE_URL}/api/discoverywebsite/LotFinder/lot_results"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"{BASE_URL}/watches",
}


def _extract_price_chf(price_data: dict) -> float | None:
    """Estrae il prezzo in CHF dalla struttura Christie's."""
    if not price_data:
        return None
    # Christie's usa una struttura con valuta e importo
    amount = price_data.get("amount") or price_data.get("estimate_amount")
    currency = (price_data.get("currency") or "").upper()

    if amount is None:
        return None

    # Converti valuta se necessario (tassi approssimativi)
    FX = {"USD": 0.88, "EUR": 0.95, "GBP": 1.12, "CHF": 1.0, "HKD": 0.113}
    rate = FX.get(currency, 1.0)
    return round(float(amount) * rate, 0)


def _normalize_lot(lot: dict) -> dict:
    """Normalizza un lotto Christie's nel formato interno."""
    result: dict[str, Any] = {
        "auction_house": "Christie's",
        "currency": "CHF",
        "buyer_premium_pct": 26.0,
    }

    # Titolo e brand
    title = lot.get("title_primary", {}).get("title", "") or lot.get("title", "")
    result["description"] = title
    result["model"] = title

    for brand in ["Rolex", "Patek Philippe", "Audemars Piguet", "F.P. Journe",
                   "Richard Mille", "Omega", "Cartier", "Vacheron Constantin",
                   "A. Lange & Söhne", "Breguet", "IWC", "Jaeger-LeCoultre"]:
        if brand.lower() in title.lower():
            result["brand"] = brand
            result["model"] = title.replace(brand, "").strip(" ,")
            break

    if "brand" not in result:
        result["brand"] = "Unknown"

    # Lot number
    result["lot_number"] = str(lot.get("lot_number", ""))

    # URL
    object_id = lot.get("object_id", "")
    sale_number = lot.get("sale_number", "")
    if object_id:
        result["lot_url"] = f"{BASE_URL}/en/lot/{object_id}-{sale_number}"

    # Prezzi
    price = lot.get("price_realized", {})
    result["hammer_price_chf"] = _extract_price_chf(price)

    est_low = lot.get("estimate_low", {})
    est_high = lot.get("estimate_high", {})
    result["estimate_low_chf"] = _extract_price_chf(est_low)
    result["estimate_high_chf"] = _extract_price_chf(est_high)

    if result.get("hammer_price_chf"):
        result["total_price_chf"] = round(result["hammer_price_chf"] * 1.26, 0)

    # Immagine
    images = lot.get("images", [])
    if images:
        result["image_url"] = images[0].get("src", "")

    # Data asta
    sale_date = lot.get("sale_date", "") or lot.get("date_auction", "")
    if sale_date and len(sale_date) >= 10:
        result["sale_date"] = sale_date[:10]
    else:
        result["sale_date"] = "2024-01-01"

    result["sale_name"] = lot.get("sale_title", "")
    result["sale_location"] = lot.get("sale_location", "")

    return result


async def scrape_recent_results(limit: int = 50) -> list[dict]:
    """
    Scarica i risultati recenti di orologi da Christie's via API JSON.
    """
    logger.info(f"Christie's scraper: fetch risultati recenti (limit={limit})")
    results = []

    params = {
        "action": "GetLotResults",
        "dept_filter": "52",  # 52 = Watches
        "sort_by": "saleDateDesc",
        "int_start": 0,
        "int_stop": min(limit, 50),
        "view_type": "listview",
    }

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        try:
            resp = await client.get(SEARCH_API, params=params)
            resp.raise_for_status()
            data = resp.json()

            lots = (
                data.get("lots", [])
                or data.get("LotResults", [])
                or data.get("results", [])
            )
            logger.info(f"Christie's API: {len(lots)} lotti ricevuti")

            for lot in lots[:limit]:
                try:
                    normalized = _normalize_lot(lot)
                    if normalized.get("brand") != "Unknown":
                        results.append(normalized)
                except Exception as e:
                    logger.debug(f"Christie's: errore normalizzazione lotto: {e}")

        except httpx.HTTPError as e:
            logger.warning(f"Christie's API non disponibile: {e} — fallback HTML")
            results = await _scrape_html_fallback(client, limit)
        except Exception as e:
            logger.error(f"Christie's scraper errore: {e}")

    logger.info(f"Christie's scraper: estratti {len(results)} risultati")
    return results


async def _scrape_html_fallback(client: httpx.AsyncClient, limit: int) -> list[dict]:
    """Fallback: scraping HTML della pagina results Christie's."""
    url = f"{BASE_URL}/en/departments/watches-52-1.aspx"
    results = []
    try:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        lot_links = []
        for a in soup.find_all("a", href=re.compile(r"/en/lot/", re.I)):
            href = a.get("href", "")
            full = href if href.startswith("http") else f"{BASE_URL}{href}"
            if full not in lot_links:
                lot_links.append(full)
            if len(lot_links) >= limit:
                break

        for url_lot in lot_links[:limit]:
            try:
                r = await client.get(url_lot)
                r.raise_for_status()
                soup_lot = BeautifulSoup(r.text, "html.parser")

                result: dict[str, Any] = {
                    "auction_house": "Christie's",
                    "lot_url": url_lot,
                    "currency": "CHF",
                    "buyer_premium_pct": 26.0,
                    "sale_date": "2024-01-01",
                    "brand": "Unknown",
                    "model": "Unknown",
                }

                h1 = soup_lot.find("h1")
                if h1:
                    result["description"] = h1.get_text(strip=True)
                    result["model"] = result["description"]

                price_el = soup_lot.find(class_=re.compile(r"price.realized|hammer", re.I))
                if price_el:
                    nums = re.findall(r"[\d,]+", price_el.get_text())
                    if nums:
                        result["hammer_price_chf"] = float(nums[0].replace(",", ""))
                        result["total_price_chf"] = round(result["hammer_price_chf"] * 1.26)

                if result["brand"] != "Unknown":
                    results.append(result)

                await asyncio.sleep(0.5)
            except Exception as e:
                logger.debug(f"Christie's HTML fallback errore {url_lot}: {e}")

    except Exception as e:
        logger.error(f"Christie's fallback errore: {e}")

    return results


async def scrape_reference(reference: str) -> list[dict]:
    """
    Cerca su Christie's i risultati per una referenza specifica.
    """
    logger.info(f"Christie's scraper: ricerca referenza '{reference}'")
    results = []

    search_url = f"{BASE_URL}/en/results"
    params = {
        "action": "GetSearchResults",
        "searchFrom": "SearchResults",
        "Ntt": reference,
        "Nrpp": 20,
    }

    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0, follow_redirects=True) as client:
        try:
            resp = await client.get(search_url, params=params)
            resp.raise_for_status()

            if resp.headers.get("content-type", "").startswith("application/json"):
                data = resp.json()
                for lot in data.get("lots", [])[:20]:
                    normalized = _normalize_lot(lot)
                    normalized["reference"] = reference
                    results.append(normalized)
            else:
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=re.compile(r"/en/lot/", re.I)):
                    href = a.get("href", "")
                    results.append({
                        "auction_house": "Christie's",
                        "reference": reference,
                        "lot_url": href if href.startswith("http") else f"{BASE_URL}{href}",
                        "sale_date": "2024-01-01",
                        "brand": "Unknown",
                        "model": reference,
                        "currency": "CHF",
                    })

        except Exception as e:
            logger.error(f"Christie's scraper ricerca '{reference}': {e}")

    return results
