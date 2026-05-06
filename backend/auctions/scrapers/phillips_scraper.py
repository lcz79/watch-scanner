"""
Phillips Watches scraper.
Sito: https://www.phillipswatches.com/auction-results/
Usa httpx + BeautifulSoup per estrarre i risultati pubblici.

Nota: Phillips ha un'API JSON parzialmente pubblica accessibile via XHR.
Proviamo prima quella, fallback su HTML parsing.
"""
import asyncio
import re
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.phillipswatches.com"
RESULTS_URL = f"{BASE_URL}/auction-results/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": BASE_URL,
}


def _parse_chf_price(text: str | None) -> float | None:
    """Estrae un prezzo in CHF da stringhe come 'CHF 432,500' o 'CHF 1,234,567'."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d.,]", "", text.replace(",", ""))
    try:
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def _parse_estimate(text: str | None) -> tuple[float | None, float | None]:
    """
    Parsa 'CHF 150,000 - 300,000' → (150000.0, 300000.0)
    o 'Estimate on Request' → (None, None)
    """
    if not text or "request" in text.lower():
        return None, None
    parts = re.findall(r"[\d,]+", text)
    if len(parts) >= 2:
        low = float(parts[0].replace(",", ""))
        high = float(parts[1].replace(",", ""))
        return low, high
    elif len(parts) == 1:
        val = float(parts[0].replace(",", ""))
        return val, val
    return None, None


def _parse_lot_page(html: str, lot_url: str) -> dict:
    """Parsa la pagina di un singolo lotto Phillips."""
    soup = BeautifulSoup(html, "html.parser")
    result: dict[str, Any] = {
        "auction_house": "Phillips",
        "lot_url": lot_url,
        "currency": "CHF",
    }

    # Titolo lotto (brand + model)
    title_el = soup.find("h1", class_=re.compile(r"lot.?title|title", re.I))
    if not title_el:
        title_el = soup.find("h1")
    if title_el:
        title_text = title_el.get_text(strip=True)
        result["description"] = title_text
        # Cerca brand noto nel titolo
        for brand in ["Rolex", "Patek Philippe", "Audemars Piguet", "F.P. Journe",
                       "Richard Mille", "Omega", "Cartier", "Vacheron Constantin",
                       "A. Lange & Söhne", "Breguet", "IWC", "Jaeger-LeCoultre"]:
            if brand.lower() in title_text.lower():
                result["brand"] = brand
                break

    # Lot number
    lot_el = soup.find(string=re.compile(r"lot\s+\d+", re.I))
    if lot_el:
        m = re.search(r"(\d+)", lot_el)
        if m:
            result["lot_number"] = m.group(1)

    # Hammer price
    hammer_el = (
        soup.find(class_=re.compile(r"hammer|sold|price.?realized", re.I))
        or soup.find(string=re.compile(r"hammer|sold for|price realized", re.I))
    )
    if hammer_el:
        result["hammer_price_chf"] = _parse_chf_price(
            hammer_el.get_text() if hasattr(hammer_el, "get_text") else str(hammer_el)
        )

    # Estimate
    est_el = soup.find(class_=re.compile(r"estimate", re.I))
    if est_el:
        low, high = _parse_estimate(est_el.get_text())
        result["estimate_low_chf"] = low
        result["estimate_high_chf"] = high

    # Calcola total con buyer premium 26%
    if result.get("hammer_price_chf"):
        result["total_price_chf"] = round(result["hammer_price_chf"] * 1.26, 0)
        result["buyer_premium_pct"] = 26.0

    # Image
    img = soup.find("img", class_=re.compile(r"lot.?image|watch.?image", re.I))
    if img and img.get("src"):
        src = img["src"]
        result["image_url"] = src if src.startswith("http") else f"{BASE_URL}{src}"

    return result


async def scrape_recent_results(limit: int = 50) -> list[dict]:
    """
    Scarica i risultati più recenti da Phillips.
    Ritorna una lista di dict normalizzati pronti per il DB.
    """
    logger.info(f"Phillips scraper: fetch risultati recenti (limit={limit})")
    results = []

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        try:
            resp = await client.get(RESULTS_URL)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Phillips scraper: errore HTTP su {RESULTS_URL}: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        # Trova tutti i link ai lotti
        lot_links = []
        for a in soup.find_all("a", href=re.compile(r"/lot/|/watch/|results.*lot", re.I)):
            href = a.get("href", "")
            full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
            if full_url not in lot_links:
                lot_links.append(full_url)
            if len(lot_links) >= limit:
                break

        logger.info(f"Phillips scraper: trovati {len(lot_links)} link lotti")

        # Scarica ogni lotto
        for url in lot_links[:limit]:
            try:
                r = await client.get(url)
                r.raise_for_status()
                lot_data = _parse_lot_page(r.text, url)
                if lot_data.get("brand"):
                    results.append(lot_data)
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.debug(f"Phillips: errore parsing lotto {url}: {e}")
                continue

    logger.info(f"Phillips scraper: estratti {len(results)} risultati")
    return results


async def scrape_reference(reference: str) -> list[dict]:
    """
    Cerca su Phillips i risultati per una referenza specifica.
    Usa la search page.
    """
    logger.info(f"Phillips scraper: ricerca referenza '{reference}'")
    search_url = f"{BASE_URL}/search/?q={reference}&type=watch"
    results = []

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        try:
            resp = await client.get(search_url)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Phillips scraper: errore ricerca {reference}: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        lot_links = []
        for a in soup.find_all("a", href=re.compile(r"/lot/|/watch/", re.I)):
            href = a.get("href", "")
            full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
            if full_url not in lot_links:
                lot_links.append(full_url)

        logger.info(f"Phillips scraper: {len(lot_links)} risultati per '{reference}'")

        for url in lot_links[:20]:
            try:
                r = await client.get(url)
                lot_data = _parse_lot_page(r.text, url)
                lot_data["reference"] = reference
                if lot_data.get("brand") or lot_data.get("description"):
                    results.append(lot_data)
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.debug(f"Phillips: errore lotto {url}: {e}")

    return results
