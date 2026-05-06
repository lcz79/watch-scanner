"""
Sotheby's Watches scraper.
Sito: https://www.sothebys.com/en/departments/watches
API: Sotheby's espone endpoint JSON per i risultati d'asta.
"""
import asyncio
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.sothebys.com"
SEARCH_API = f"{BASE_URL}/api/search/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"{BASE_URL}/en/departments/watches",
    "x-requested-with": "XMLHttpRequest",
}

# Tasso di cambio approssimativo verso CHF
FX_TO_CHF = {
    "USD": 0.88,
    "EUR": 0.95,
    "GBP": 1.12,
    "CHF": 1.0,
    "HKD": 0.113,
}


def _to_chf(amount: float | None, currency: str = "CHF") -> float | None:
    if amount is None:
        return None
    rate = FX_TO_CHF.get(currency.upper(), 1.0)
    return round(amount * rate, 0)


def _parse_sothebys_lot(lot: dict) -> dict:
    """Normalizza un lotto Sotheby's nel formato interno."""
    result: dict[str, Any] = {
        "auction_house": "Sotheby's",
        "currency": "CHF",
        "buyer_premium_pct": 26.0,
    }

    # Titolo
    title = (
        lot.get("title", "")
        or lot.get("heading", "")
        or lot.get("primaryTitle", "")
    )
    result["description"] = title
    result["model"] = title

    for brand in ["Rolex", "Patek Philippe", "Audemars Piguet", "F.P. Journe",
                   "Richard Mille", "Omega", "Cartier", "Vacheron Constantin",
                   "A. Lange & Söhne", "Breguet", "IWC", "Jaeger-LeCoultre"]:
        if brand.lower() in title.lower():
            result["brand"] = brand
            result["model"] = title.replace(brand, "").strip(" ,.-")
            break

    if "brand" not in result:
        result["brand"] = "Unknown"

    # Lot number
    result["lot_number"] = str(lot.get("lotNumber", lot.get("lot", "")))

    # URL
    url_path = lot.get("url", lot.get("detailUrl", ""))
    result["lot_url"] = url_path if url_path.startswith("http") else f"{BASE_URL}{url_path}"

    # Data asta
    for date_field in ["saleDate", "date", "eventDate", "auctionDate"]:
        date_val = lot.get(date_field, "")
        if date_val and len(str(date_val)) >= 10:
            result["sale_date"] = str(date_val)[:10]
            break
    if "sale_date" not in result:
        result["sale_date"] = "2024-01-01"

    result["sale_name"] = lot.get("saleName", lot.get("saleTitle", ""))
    result["sale_location"] = lot.get("saleLocation", lot.get("location", ""))

    # Prezzi
    currency = lot.get("currency", "CHF").upper()

    hammer_raw = (
        lot.get("priceRealizedUSD")
        or lot.get("hammer_price")
        or lot.get("hammerPrice")
        or lot.get("priceRealized")
    )
    if hammer_raw:
        try:
            hammer_chf = _to_chf(float(str(hammer_raw).replace(",", "")), currency)
            result["hammer_price_chf"] = hammer_chf
            if hammer_chf:
                result["total_price_chf"] = round(hammer_chf * 1.26, 0)
        except (ValueError, TypeError):
            pass

    est_low_raw = lot.get("estimateLow", lot.get("estimate_low"))
    est_high_raw = lot.get("estimateHigh", lot.get("estimate_high"))
    if est_low_raw:
        try:
            result["estimate_low_chf"] = _to_chf(float(str(est_low_raw).replace(",", "")), currency)
        except (ValueError, TypeError):
            pass
    if est_high_raw:
        try:
            result["estimate_high_chf"] = _to_chf(float(str(est_high_raw).replace(",", "")), currency)
        except (ValueError, TypeError):
            pass

    # Immagine
    images = lot.get("images", lot.get("media", []))
    if images and isinstance(images, list) and len(images) > 0:
        img = images[0]
        result["image_url"] = img.get("src", img.get("url", "")) if isinstance(img, dict) else str(img)

    return result


async def scrape_recent_results(limit: int = 50) -> list[dict]:
    """Scarica i risultati più recenti da Sotheby's."""
    logger.info(f"Sotheby's scraper: fetch risultati recenti (limit={limit})")
    results = []

    payload = {
        "query": "watch",
        "department": "Watches",
        "type": "lot",
        "keyword": "luxury watch",
        "sort": "date_desc",
        "from": 0,
        "size": min(limit, 50),
    }

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        try:
            resp = await client.post(SEARCH_API, json=payload)
            resp.raise_for_status()
            data = resp.json()

            lots = (
                data.get("lots", [])
                or data.get("items", [])
                or data.get("results", [])
                or data.get("data", {}).get("lots", [])
            )
            logger.info(f"Sotheby's API: {len(lots)} lotti")

            for lot in lots[:limit]:
                try:
                    normalized = _parse_sothebys_lot(lot)
                    if normalized.get("brand") != "Unknown":
                        results.append(normalized)
                except Exception as e:
                    logger.debug(f"Sotheby's errore normalizzazione: {e}")

        except httpx.HTTPError as e:
            logger.warning(f"Sotheby's API non raggiungibile: {e} — fallback HTML")
            results = await _scrape_html_fallback(client, limit)
        except Exception as e:
            logger.error(f"Sotheby's scraper errore: {e}")

    logger.info(f"Sotheby's scraper: estratti {len(results)} risultati")
    return results


async def _scrape_html_fallback(client: httpx.AsyncClient, limit: int) -> list[dict]:
    """Fallback HTML per Sotheby's."""
    url = f"{BASE_URL}/en/departments/watches"
    results = []
    try:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        lot_links = []
        for a in soup.find_all("a", href=re.compile(r"/en/buy/auction/|/lot/", re.I)):
            href = a.get("href", "")
            full = href if href.startswith("http") else f"{BASE_URL}{href}"
            if full not in lot_links:
                lot_links.append(full)
            if len(lot_links) >= limit:
                break

        logger.info(f"Sotheby's HTML fallback: {len(lot_links)} link lotti")

        for lot_url in lot_links[:limit]:
            try:
                r = await client.get(lot_url)
                r.raise_for_status()
                soup_lot = BeautifulSoup(r.text, "html.parser")

                result: dict[str, Any] = {
                    "auction_house": "Sotheby's",
                    "lot_url": lot_url,
                    "currency": "CHF",
                    "buyer_premium_pct": 26.0,
                    "sale_date": "2024-01-01",
                    "brand": "Unknown",
                    "model": "Unknown",
                }

                h1 = soup_lot.find("h1")
                if h1:
                    result["description"] = h1.get_text(strip=True)

                price_el = soup_lot.find(
                    class_=re.compile(r"price.realized|hammer.price|sold.for", re.I)
                )
                if price_el:
                    nums = re.findall(r"[\d,]+", price_el.get_text())
                    if nums:
                        result["hammer_price_chf"] = float(nums[0].replace(",", ""))
                        result["total_price_chf"] = round(result["hammer_price_chf"] * 1.26)

                results.append(result)
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.debug(f"Sotheby's HTML errore {lot_url}: {e}")

    except Exception as e:
        logger.error(f"Sotheby's HTML fallback errore: {e}")

    return results


async def scrape_reference(reference: str) -> list[dict]:
    """Cerca su Sotheby's i risultati per una referenza specifica."""
    logger.info(f"Sotheby's scraper: ricerca referenza '{reference}'")
    results = []

    search_url = f"{BASE_URL}/en/results"
    params = {"keyword": reference, "type": "lot"}

    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0, follow_redirects=True) as client:
        try:
            resp = await client.get(search_url, params=params)
            resp.raise_for_status()

            if "application/json" in resp.headers.get("content-type", ""):
                data = resp.json()
                for lot in (data.get("lots", []) or data.get("results", []))[:20]:
                    normalized = _parse_sothebys_lot(lot)
                    normalized["reference"] = reference
                    results.append(normalized)
            else:
                # HTML: estrai link lotti
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=re.compile(r"/en/buy/auction/|/lot/", re.I)):
                    href = a.get("href", "")
                    results.append({
                        "auction_house": "Sotheby's",
                        "reference": reference,
                        "lot_url": href if href.startswith("http") else f"{BASE_URL}{href}",
                        "sale_date": "2024-01-01",
                        "brand": "Unknown",
                        "model": reference,
                        "currency": "CHF",
                    })

        except Exception as e:
            logger.error(f"Sotheby's scraper ricerca '{reference}': {e}")

    return results
