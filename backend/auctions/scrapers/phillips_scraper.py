"""
Phillips Watches scraper — REWRITE con Playwright.
Sito: https://www.phillipswatches.com/auction-results/

Usa Playwright per gestire il rendering JS della SPA.
"""
import asyncio
import json
import re
from datetime import datetime
from typing import Any

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.phillipswatches.com"
RESULTS_URL = f"{BASE_URL}/auction-results/"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

KNOWN_BRANDS = [
    "Rolex", "Patek Philippe", "Audemars Piguet", "F.P. Journe",
    "Richard Mille", "Omega", "Cartier", "Vacheron Constantin",
    "A. Lange & Söhne", "Breguet", "IWC", "Jaeger-LeCoultre",
    "Panerai", "Hublot", "Tudor", "Zenith", "Chopard", "Girard-Perregaux",
    "Lange & Söhne", "AP", "Ulysse Nardin", "Roger Dubuis",
]


def _extract_brand(text: str) -> str:
    """Estrae il brand da un testo."""
    text_lower = text.lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in text_lower:
            return brand
    return "Unknown"


def _parse_chf_price(text: str | None) -> float | None:
    """Estrae un prezzo da stringhe come 'CHF 432,500' o '1,234,567'."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d]", "", text.replace(",", "").replace(".", ""))
    try:
        return float(cleaned) if cleaned else None
    except (ValueError, AttributeError):
        return None


def _parse_estimate(text: str | None) -> tuple[float | None, float | None]:
    """
    Parsa 'CHF 150,000 - 300,000' → (150000.0, 300000.0)
    o 'Estimate on Request' → (None, None)
    """
    if not text or "request" in text.lower():
        return None, None
    # Estrai tutti i numeri
    parts = re.findall(r"[\d,]+", text)
    nums = []
    for p in parts:
        try:
            v = float(p.replace(",", ""))
            if v > 100:  # filtra numeri piccoli che non sono prezzi
                nums.append(v)
        except ValueError:
            pass
    if len(nums) >= 2:
        return nums[0], nums[1]
    elif len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def _extract_lot_data_from_json(json_data: dict, lot_url: str) -> dict | None:
    """Estrae i dati del lotto da struttura JSON (Next.js o API)."""
    result: dict[str, Any] = {
        "auction_house": "Phillips",
        "lot_url": lot_url,
        "currency": "CHF",
        "buyer_premium_pct": 26.0,
    }

    # Cerca i dati del lotto in vari percorsi
    lot = (
        json_data.get("lot") or json_data.get("lotData")
        or json_data.get("props", {}).get("pageProps", {}).get("lot")
        or json_data.get("props", {}).get("pageProps", {}).get("lotData")
        or json_data
    )

    if not lot or not isinstance(lot, dict):
        return None

    # Titolo / descrizione
    title = (
        lot.get("title") or lot.get("lotTitle") or lot.get("description")
        or lot.get("name") or lot.get("watchTitle") or ""
    )
    result["description"] = str(title)

    # Brand
    brand_raw = lot.get("maker") or lot.get("brand") or lot.get("manufacturer") or ""
    if brand_raw:
        result["brand"] = str(brand_raw)
    else:
        result["brand"] = _extract_brand(str(title))

    # Model
    model_raw = lot.get("model") or lot.get("watchModel") or lot.get("denomination") or title
    result["model"] = str(model_raw)

    # Reference
    ref_raw = (
        lot.get("reference") or lot.get("refNo") or lot.get("catalogueRef")
        or lot.get("referenceNumber") or ""
    )
    result["reference"] = str(ref_raw)

    # Lot number
    lot_num = lot.get("lotNumber") or lot.get("lot") or lot.get("lotNum") or ""
    result["lot_number"] = str(lot_num)

    # Hammer price
    hammer_raw = (
        lot.get("hammerPrice") or lot.get("soldPrice") or lot.get("priceRealized")
        or lot.get("salePrice") or lot.get("result")
    )
    if isinstance(hammer_raw, (int, float)):
        result["hammer_price_chf"] = float(hammer_raw)
    elif isinstance(hammer_raw, str):
        result["hammer_price_chf"] = _parse_chf_price(hammer_raw)

    # Stima
    est_low = lot.get("estimateLow") or lot.get("lowEstimate")
    est_high = lot.get("estimateHigh") or lot.get("highEstimate")
    if isinstance(est_low, (int, float)):
        result["estimate_low_chf"] = float(est_low)
    if isinstance(est_high, (int, float)):
        result["estimate_high_chf"] = float(est_high)

    if not result.get("estimate_low_chf") and not result.get("estimate_high_chf"):
        est_str = lot.get("estimate") or lot.get("estimateString") or ""
        low, high = _parse_estimate(str(est_str))
        result["estimate_low_chf"] = low
        result["estimate_high_chf"] = high

    # Total price
    if result.get("hammer_price_chf"):
        result["total_price_chf"] = round(result["hammer_price_chf"] * 1.26, 0)

    # Sale info
    sale = lot.get("sale") or lot.get("auction") or {}
    if isinstance(sale, dict):
        result["sale_name"] = str(sale.get("title") or sale.get("name") or "")
        result["sale_location"] = str(sale.get("location") or sale.get("city") or "")
        date_raw = sale.get("date") or sale.get("saleDate") or ""
        if date_raw:
            result["sale_date"] = str(date_raw)[:10]

    # Date fallback
    if not result.get("sale_date"):
        date_raw = lot.get("saleDate") or lot.get("date") or lot.get("auctionDate") or ""
        result["sale_date"] = str(date_raw)[:10] if date_raw else datetime.utcnow().strftime("%Y-%m-%d")

    # Immagine
    img_raw = (
        lot.get("imageUrl") or lot.get("image") or lot.get("photo")
        or lot.get("photoPath") or lot.get("thumbnailUrl")
    )
    if isinstance(img_raw, str):
        result["image_url"] = img_raw if img_raw.startswith("http") else f"{BASE_URL}{img_raw}"
    elif isinstance(img_raw, list) and img_raw:
        first_img = img_raw[0]
        src = first_img.get("url") or first_img.get("src") or str(first_img)
        result["image_url"] = src if src.startswith("http") else f"{BASE_URL}{src}"

    return result if result.get("brand") or result.get("description") else None


def _parse_lot_page_html(html: str, lot_url: str) -> dict | None:
    """Parsa la pagina HTML di un lotto Phillips come fallback."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    result: dict[str, Any] = {
        "auction_house": "Phillips",
        "lot_url": lot_url,
        "currency": "CHF",
        "buyer_premium_pct": 26.0,
    }

    # Titolo h1
    title_el = soup.find("h1") or soup.find(class_=re.compile(r"lot.?title|title", re.I))
    title = title_el.get_text(strip=True) if title_el else ""
    result["description"] = title
    result["brand"] = _extract_brand(title)
    result["model"] = title

    if not title and not result["brand"]:
        return None

    # Lot number
    lot_el = soup.find(string=re.compile(r"lot\s+\d+", re.I))
    if lot_el:
        m = re.search(r"(\d+)", str(lot_el))
        if m:
            result["lot_number"] = m.group(1)

    # Reference
    ref_el = soup.find(string=re.compile(r"ref\.?\s*[\w\-/]+", re.I))
    if ref_el:
        m = re.search(r"ref\.?\s*([\w\-/]+)", str(ref_el), re.I)
        if m:
            result["reference"] = m.group(1)

    # Hammer price
    for el in soup.find_all(class_=re.compile(r"hammer|sold|price.?realized|result", re.I)):
        price = _parse_chf_price(el.get_text())
        if price and price > 1000:
            result["hammer_price_chf"] = price
            result["total_price_chf"] = round(price * 1.26, 0)
            break

    # Stima
    for el in soup.find_all(class_=re.compile(r"estimate", re.I)):
        low, high = _parse_estimate(el.get_text())
        if low or high:
            result["estimate_low_chf"] = low
            result["estimate_high_chf"] = high
            break

    # Sale info
    for el in soup.find_all(class_=re.compile(r"sale.?info|auction.?info|sale.?details", re.I)):
        text = el.get_text()
        # Data
        m = re.search(r"\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4}", text)
        if m:
            result["sale_date"] = m.group(0)[:10]
        # Location
        for city in ["Geneva", "Hong Kong", "New York", "London", "Paris"]:
            if city.lower() in text.lower():
                result["sale_location"] = city
                break

    if not result.get("sale_date"):
        result["sale_date"] = datetime.utcnow().strftime("%Y-%m-%d")

    # Image
    img = (
        soup.find("img", class_=re.compile(r"lot.?image|watch.?image|main.?image", re.I))
        or soup.find("img", id=re.compile(r"main|lot|watch", re.I))
    )
    if img and img.get("src"):
        src = img["src"]
        result["image_url"] = src if src.startswith("http") else f"{BASE_URL}{src}"

    return result if result.get("model") or result.get("brand") else None


async def _scrape_lot_page(page, lot_url: str) -> dict | None:
    """
    Scarica e parsa una singola pagina lotto con Playwright.
    Prima cerca in __NEXT_DATA__, poi fallback HTML.
    """
    try:
        await page.goto(lot_url, wait_until="networkidle", timeout=20000)
        await asyncio.sleep(1)

        # Tenta __NEXT_DATA__
        next_data_raw = await page.evaluate(
            "() => { try { return JSON.stringify(window.__NEXT_DATA__); } catch(e) { return null; } }"
        )
        if next_data_raw:
            try:
                next_data = json.loads(next_data_raw)
                lot_data = _extract_lot_data_from_json(next_data, lot_url)
                if lot_data:
                    return lot_data
            except json.JSONDecodeError:
                pass

        # Fallback HTML
        html = await page.content()
        return _parse_lot_page_html(html, lot_url)

    except Exception as e:
        logger.debug(f"Phillips: errore parsing lotto {lot_url}: {e}")
        return None


async def scrape_recent_results(limit: int = 50) -> list[dict]:
    """
    Scarica i risultati più recenti da Phillips usando Playwright.
    Ritorna lista di dict normalizzati per il DB.
    """
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup

    logger.info(f"Phillips scraper (Playwright): fetch risultati recenti (limit={limit})")
    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 900},
            )
            page = await context.new_page()

            try:
                # Carica la pagina dei risultati
                await page.goto(RESULTS_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                # Cerca sale (aste con risultati pubblicati)
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Trova link alle singole sale (es. /auction/xxx/results)
                sale_links = []
                for a in soup.find_all("a", href=True):
                    href = a.get("href", "")
                    if re.search(r"/auction/|/sale/", href, re.I) and "result" not in href.lower():
                        full = href if href.startswith("http") else f"{BASE_URL}{href}"
                        if full not in sale_links:
                            sale_links.append(full)

                # Trova anche link diretti a lotti
                lot_links = []
                for a in soup.find_all("a", href=True):
                    href = a.get("href", "")
                    if re.search(r"/lot/|/watch/\d+", href, re.I):
                        full = href if href.startswith("http") else f"{BASE_URL}{href}"
                        if full not in lot_links:
                            lot_links.append(full)

                logger.info(f"Phillips: {len(sale_links)} sale, {len(lot_links)} lot links trovati")

                # Se ci sono sale, entra nella prima e recupera lotti
                if sale_links and not lot_links:
                    for sale_url in sale_links[:3]:
                        try:
                            await page.goto(sale_url, wait_until="networkidle", timeout=20000)
                            await asyncio.sleep(1)
                            sale_html = await page.content()
                            sale_soup = BeautifulSoup(sale_html, "html.parser")
                            for a in sale_soup.find_all("a", href=True):
                                href = a.get("href", "")
                                if re.search(r"/lot/|/watch/\d+", href, re.I):
                                    full = href if href.startswith("http") else f"{BASE_URL}{href}"
                                    if full not in lot_links:
                                        lot_links.append(full)
                        except Exception as e:
                            logger.debug(f"Phillips: errore navigazione sale {sale_url}: {e}")

                logger.info(f"Phillips: {len(lot_links)} lotti totali trovati")

                # Scarica ogni lotto
                for lot_url in lot_links[:limit]:
                    lot_data = await _scrape_lot_page(page, lot_url)
                    if lot_data and (lot_data.get("brand") or lot_data.get("description")):
                        if lot_data.get("brand", "Unknown") != "Unknown" or lot_data.get("model"):
                            results.append(lot_data)
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Phillips scraper: errore principale: {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Phillips scraper: errore Playwright: {e}")

    logger.info(f"Phillips scraper: estratti {len(results)} risultati")
    return results


async def scrape_reference(reference: str) -> list[dict]:
    """
    Cerca su Phillips i risultati per una referenza specifica.
    """
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup

    logger.info(f"Phillips scraper: ricerca referenza '{reference}'")
    search_url = f"{BASE_URL}/search/?q={reference}&type=watch"
    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 900},
            )
            page = await context.new_page()

            try:
                await page.goto(search_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                lot_links = []
                for a in soup.find_all("a", href=True):
                    href = a.get("href", "")
                    if re.search(r"/lot/|/watch/\d+", href, re.I):
                        full = href if href.startswith("http") else f"{BASE_URL}{href}"
                        if full not in lot_links:
                            lot_links.append(full)

                logger.info(f"Phillips: {len(lot_links)} risultati per '{reference}'")

                for lot_url in lot_links[:20]:
                    lot_data = await _scrape_lot_page(page, lot_url)
                    if lot_data:
                        lot_data["reference"] = reference
                        results.append(lot_data)
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Phillips: errore ricerca '{reference}': {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Phillips: errore Playwright ricerca: {e}")

    return results
