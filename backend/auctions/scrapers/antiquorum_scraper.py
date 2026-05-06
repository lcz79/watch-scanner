"""
Antiquorum scraper.
Sito: https://www.antiquorum.swiss/auction-results
Antiquorum ha un sito più semplice con HTML parsabile.
"""
import asyncio
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.antiquorum.swiss"
RESULTS_URL = f"{BASE_URL}/en/auction-results"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": BASE_URL,
}

FX_TO_CHF = {
    "CHF": 1.0,
    "USD": 0.88,
    "EUR": 0.95,
    "GBP": 1.12,
    "HKD": 0.113,
}

KNOWN_BRANDS = [
    "Rolex", "Patek Philippe", "Audemars Piguet", "F.P. Journe",
    "Richard Mille", "Omega", "Cartier", "Vacheron Constantin",
    "A. Lange & Söhne", "Breguet", "IWC", "Jaeger-LeCoultre",
    "Girard-Perregaux", "Ulysse Nardin", "Blancpain", "Tudor",
    "Longines", "Zenith", "TAG Heuer", "Hublot", "Panerai",
]


def _detect_brand(text: str) -> str | None:
    for brand in KNOWN_BRANDS:
        if brand.lower() in text.lower():
            return brand
    return None


def _parse_price_string(text: str) -> float | None:
    """Parsa 'CHF 432,500' o 'CHF 1.234.567' o 'USD 180,000'."""
    if not text or text.strip() in ("", "N/A", "-", "Estimate on Request"):
        return None

    # Trova valuta
    currency = "CHF"
    for cur in FX_TO_CHF:
        if cur in text.upper():
            currency = cur
            break

    # Estrai numero
    nums = re.findall(r"[\d]+", text.replace(",", "").replace(".", ""))
    if not nums:
        return None
    try:
        amount = float("".join(nums[:2]) if len(nums) > 2 else nums[0])
        # Sanity check: ignora numeri troppo piccoli (lotti inerti)
        if amount < 100:
            return None
        return round(amount * FX_TO_CHF.get(currency, 1.0), 0)
    except ValueError:
        return None


def _parse_lot_page(html: str, url: str) -> dict:
    """Parsa la pagina HTML di un singolo lotto Antiquorum."""
    soup = BeautifulSoup(html, "html.parser")
    result: dict[str, Any] = {
        "auction_house": "Antiquorum",
        "lot_url": url,
        "currency": "CHF",
        "buyer_premium_pct": 26.0,
        "sale_date": "2024-01-01",
    }

    # Titolo principale
    title_el = soup.find("h1") or soup.find(class_=re.compile(r"lot.?title|item.?title", re.I))
    title = title_el.get_text(strip=True) if title_el else ""
    result["description"] = title

    brand = _detect_brand(title)
    result["brand"] = brand or "Unknown"
    result["model"] = title.replace(brand, "").strip(" ,.-") if brand else title

    # Lot number
    lot_el = soup.find(string=re.compile(r"lot\s*[:#]?\s*\d+", re.I))
    if lot_el:
        m = re.search(r"(\d+)", str(lot_el))
        if m:
            result["lot_number"] = m.group(1)

    # Dati strutturati in tabella o lista definizioni
    details = {}
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) == 2:
            key = cells[0].get_text(strip=True).lower()
            val = cells[1].get_text(strip=True)
            details[key] = val

    for dl in soup.find_all("dl"):
        terms = dl.find_all("dt")
        defs = dl.find_all("dd")
        for t, d in zip(terms, defs):
            details[t.get_text(strip=True).lower()] = d.get_text(strip=True)

    # Referenza
    for k in ("reference", "ref.", "ref", "referenz"):
        if k in details:
            result["reference"] = details[k]
            break

    # Anno
    for k in ("year", "anno", "year made", "circa"):
        if k in details:
            result["year_made"] = details[k]
            break

    # Stima
    for k in ("estimate", "stima", "estimation"):
        if k in details:
            low, high = _parse_estimate_str(details[k])
            result["estimate_low_chf"] = low
            result["estimate_high_chf"] = high
            break

    # Hammer
    for k in ("hammer price", "sold for", "price realized", "prezzo"):
        if k in details:
            result["hammer_price_chf"] = _parse_price_string(details[k])
            if result["hammer_price_chf"]:
                result["total_price_chf"] = round(result["hammer_price_chf"] * 1.26)
            break

    # Fallback: cerca prezzi nel testo
    if not result.get("hammer_price_chf"):
        for el in soup.find_all(class_=re.compile(r"hammer|sold|price.realized|result", re.I)):
            val = _parse_price_string(el.get_text())
            if val and val > 1000:
                result["hammer_price_chf"] = val
                result["total_price_chf"] = round(val * 1.26)
                break

    # Data asta
    date_el = soup.find(class_=re.compile(r"sale.?date|auction.?date|date", re.I))
    if date_el:
        date_text = date_el.get_text(strip=True)
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_text)
        if m:
            result["sale_date"] = m.group(0)

    # Sale name
    sale_el = soup.find(class_=re.compile(r"sale.?name|sale.?title|auction.?name", re.I))
    if sale_el:
        result["sale_name"] = sale_el.get_text(strip=True)

    # Immagine
    img = soup.find("img", class_=re.compile(r"lot.?image|main.?image|watch", re.I))
    if not img:
        img = soup.find("img", src=re.compile(r"lot|watch|image", re.I))
    if img and img.get("src"):
        src = img["src"]
        result["image_url"] = src if src.startswith("http") else f"{BASE_URL}{src}"

    return result


def _parse_estimate_str(text: str) -> tuple[float | None, float | None]:
    """Parsa 'CHF 150,000 - 300,000'."""
    if not text or "request" in text.lower():
        return None, None
    nums = re.findall(r"[\d,]+", text)
    if len(nums) >= 2:
        try:
            low = float(nums[0].replace(",", ""))
            high = float(nums[1].replace(",", ""))
            return low, high
        except ValueError:
            pass
    elif len(nums) == 1:
        try:
            val = float(nums[0].replace(",", ""))
            return val, val
        except ValueError:
            pass
    return None, None


async def scrape_recent_results(limit: int = 50) -> list[dict]:
    """Scarica i risultati più recenti da Antiquorum."""
    logger.info(f"Antiquorum scraper: fetch risultati (limit={limit})")
    results = []

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        try:
            resp = await client.get(RESULTS_URL)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Antiquorum: link ai singoli lotti
            lot_links = []
            for a in soup.find_all("a", href=re.compile(r"/lot/|/en/lot/|results.*\d+", re.I)):
                href = a.get("href", "")
                full = href if href.startswith("http") else f"{BASE_URL}{href}"
                if full not in lot_links and "/lot/" in full.lower():
                    lot_links.append(full)
                if len(lot_links) >= limit:
                    break

            # Se non troviamo link /lot/, proviamo link generici
            if not lot_links:
                for a in soup.find_all("a", href=re.compile(r"\d{3,}$")):
                    href = a.get("href", "")
                    full = href if href.startswith("http") else f"{BASE_URL}{href}"
                    if full not in lot_links:
                        lot_links.append(full)
                    if len(lot_links) >= limit:
                        break

            logger.info(f"Antiquorum: {len(lot_links)} link lotti")

            for url in lot_links[:limit]:
                try:
                    r = await client.get(url)
                    r.raise_for_status()
                    lot_data = _parse_lot_page(r.text, url)
                    if lot_data.get("brand") and lot_data["brand"] != "Unknown":
                        results.append(lot_data)
                    await asyncio.sleep(0.4)
                except Exception as e:
                    logger.debug(f"Antiquorum errore lotto {url}: {e}")

        except httpx.HTTPError as e:
            logger.error(f"Antiquorum scraper HTTP errore: {e}")
        except Exception as e:
            logger.error(f"Antiquorum scraper errore: {e}")

    logger.info(f"Antiquorum: estratti {len(results)} risultati")
    return results


async def scrape_reference(reference: str) -> list[dict]:
    """Cerca su Antiquorum i risultati per una referenza specifica."""
    logger.info(f"Antiquorum scraper: ricerca '{reference}'")
    search_url = f"{BASE_URL}/en/search"
    results = []

    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0, follow_redirects=True) as client:
        try:
            resp = await client.get(search_url, params={"q": reference, "type": "lot"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            lot_links = []
            for a in soup.find_all("a", href=re.compile(r"/lot/|/en/lot/", re.I)):
                href = a.get("href", "")
                full = href if href.startswith("http") else f"{BASE_URL}{href}"
                if full not in lot_links:
                    lot_links.append(full)

            for url in lot_links[:20]:
                try:
                    r = await client.get(url)
                    lot_data = _parse_lot_page(r.text, url)
                    lot_data["reference"] = reference
                    results.append(lot_data)
                    await asyncio.sleep(0.4)
                except Exception as e:
                    logger.debug(f"Antiquorum ricerca errore {url}: {e}")

        except Exception as e:
            logger.error(f"Antiquorum scraper ricerca '{reference}': {e}")

    return results
