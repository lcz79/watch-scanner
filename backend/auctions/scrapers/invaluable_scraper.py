"""
Invaluable.com scraper — aggregatore aste con dati da centinaia di case.
Usa Playwright per gestire il JS rendering.

URL risultati: https://www.invaluable.com/search/?query={reference}&upcoming=false&resultsView=list
URL upcoming:  https://www.invaluable.com/search/?query=watches&upcoming=true
"""
import asyncio
import json
import re
from datetime import datetime
from typing import Any

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.invaluable.com"
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
]


def _extract_brand(title: str) -> str:
    """Estrae il brand dal titolo del lotto."""
    title_lower = title.lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in title_lower:
            return brand
    return "Unknown"


def _parse_price(text: str | None) -> float | None:
    """Converte stringhe prezzo tipo 'CHF 12,500' o '$8,000' in float."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d.]", "", text.replace(",", ""))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _parse_estimate(text: str | None) -> tuple[float | None, float | None]:
    """
    Parsa stime tipo 'CHF 10,000 - 15,000' → (10000.0, 15000.0).
    """
    if not text or "request" in text.lower():
        return None, None
    parts = re.findall(r"[\d,]+", text)
    nums = []
    for p in parts:
        try:
            nums.append(float(p.replace(",", "")))
        except ValueError:
            pass
    if len(nums) >= 2:
        return nums[0], nums[1]
    elif len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def _extract_from_next_data(next_data: dict, limit: int) -> list[dict]:
    """Estrae i lotti dalla struttura window.__NEXT_DATA__."""
    results = []
    try:
        # Cerca i lotti in vari percorsi tipici di Next.js
        props = next_data.get("props", {})
        page_props = props.get("pageProps", {})

        # Percorso 1: searchResults
        items = (
            page_props.get("searchResults", {}).get("results", [])
            or page_props.get("results", [])
            or page_props.get("lots", [])
            or page_props.get("items", [])
        )

        # Percorso 2: initialState Redux
        if not items:
            initial_state = page_props.get("initialState", {})
            items = (
                initial_state.get("search", {}).get("results", [])
                or initial_state.get("lots", {}).get("items", [])
            )

        for item in items[:limit]:
            lot = _normalize_invaluable_item(item)
            if lot:
                results.append(lot)

    except Exception as e:
        logger.debug(f"Invaluable __NEXT_DATA__ parse error: {e}")

    return results


def _normalize_invaluable_item(item: dict) -> dict | None:
    """Normalizza un lotto Invaluable nel formato DB."""
    try:
        title = (
            item.get("lotTitle") or item.get("title") or item.get("description") or ""
        )
        if not title:
            return None

        brand = _extract_brand(title)

        # Prezzo martello
        hammer_raw = (
            item.get("priceResult") or item.get("hammerPrice")
            or item.get("soldPrice") or item.get("price")
        )
        hammer = None
        if isinstance(hammer_raw, (int, float)):
            hammer = float(hammer_raw)
        elif isinstance(hammer_raw, str):
            hammer = _parse_price(hammer_raw)

        # Stima
        est_raw = item.get("estimateLow") or item.get("estimate") or item.get("lowEstimate")
        est_high_raw = item.get("estimateHigh") or item.get("highEstimate")
        estimate_low = float(est_raw) if isinstance(est_raw, (int, float)) else _parse_price(str(est_raw) if est_raw else None)
        estimate_high = float(est_high_raw) if isinstance(est_high_raw, (int, float)) else _parse_price(str(est_high_raw) if est_high_raw else None)

        if not estimate_low and not estimate_high:
            est_str = item.get("estimateString") or item.get("estimateRange") or ""
            estimate_low, estimate_high = _parse_estimate(str(est_str))

        # Data
        sale_date = (
            item.get("saleDate") or item.get("auctionDate")
            or item.get("date") or item.get("eventDate") or ""
        )
        if sale_date:
            # Normalizza la data in ISO
            try:
                if "T" in str(sale_date):
                    sale_date = str(sale_date)[:10]
                else:
                    sale_date = str(sale_date)[:10]
            except Exception:
                pass

        # Casa d'aste
        auction_house = (
            item.get("auctionHouse") or item.get("houseName")
            or item.get("organization") or item.get("sellerName") or "Invaluable"
        )

        # URL lotto
        lot_url = item.get("lotRef") or item.get("url") or item.get("link") or ""
        if lot_url and not lot_url.startswith("http"):
            lot_url = f"{BASE_URL}{lot_url}"

        # Immagine
        image_url = (
            item.get("photoPath") or item.get("imageUrl") or item.get("thumbnailUrl")
            or item.get("image") or ""
        )

        # Lot number
        lot_number = str(item.get("lotNum") or item.get("lotNumber") or item.get("lot") or "")

        # Sale name
        sale_name = (
            item.get("saleName") or item.get("auctionTitle") or item.get("eventTitle") or ""
        )

        result = {
            "auction_house": str(auction_house),
            "sale_name": str(sale_name),
            "sale_location": str(item.get("location") or item.get("city") or ""),
            "sale_date": str(sale_date) if sale_date else datetime.utcnow().strftime("%Y-%m-%d"),
            "lot_number": lot_number,
            "brand": brand,
            "model": str(title),
            "reference": str(item.get("reference") or item.get("refNo") or ""),
            "description": str(title),
            "estimate_low_chf": estimate_low,
            "estimate_high_chf": estimate_high,
            "hammer_price_chf": hammer,
            "buyer_premium_pct": 26.0,
            "total_price_chf": round(hammer * 1.26, 0) if hammer else None,
            "currency": str(item.get("currency") or "USD"),
            "lot_url": str(lot_url),
            "image_url": str(image_url),
        }
        return result

    except Exception as e:
        logger.debug(f"Invaluable normalize item error: {e}")
        return None


def _parse_dom_results(html_content: str, limit: int) -> list[dict]:
    """
    Fallback: parsa il DOM HTML per estrarre i lotti.
    Usato se __NEXT_DATA__ non contiene i dati.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    results = []

    # Selettori tipici di Invaluable
    selectors = [
        "div.result-item", "div.lot-item", "article.lot",
        "div[data-lot]", "div.search-result", "li.result-item",
    ]

    items = []
    for sel in selectors:
        items = soup.select(sel)
        if items:
            break

    if not items:
        # Cerca tutti i link che sembrano lotti
        items = soup.find_all("a", href=re.compile(r"/auction-results/|/lot/|/buy/", re.I))

    for item in items[:limit]:
        try:
            title_el = (
                item.find(class_=re.compile(r"title|name|description", re.I))
                or item.find("h2") or item.find("h3") or item
            )
            title = title_el.get_text(strip=True) if hasattr(title_el, "get_text") else ""
            if not title:
                continue

            brand = _extract_brand(title)

            price_el = item.find(class_=re.compile(r"price|hammer|sold|result", re.I))
            hammer = _parse_price(price_el.get_text() if price_el else None)

            est_el = item.find(class_=re.compile(r"estimate|est", re.I))
            low, high = _parse_estimate(est_el.get_text() if est_el else None)

            house_el = item.find(class_=re.compile(r"house|auction.?house|seller", re.I))
            auction_house = house_el.get_text(strip=True) if house_el else "Invaluable"

            date_el = item.find(class_=re.compile(r"date|time", re.I))
            sale_date = date_el.get_text(strip=True) if date_el else datetime.utcnow().strftime("%Y-%m-%d")

            href = item.get("href", "") if item.name == "a" else (item.find("a") or {}).get("href", "")
            lot_url = href if href.startswith("http") else f"{BASE_URL}{href}" if href else ""

            img = item.find("img")
            image_url = img.get("src", "") if img else ""

            results.append({
                "auction_house": auction_house,
                "sale_date": sale_date,
                "lot_number": "",
                "brand": brand,
                "model": title,
                "description": title,
                "estimate_low_chf": low,
                "estimate_high_chf": high,
                "hammer_price_chf": hammer,
                "buyer_premium_pct": 26.0,
                "total_price_chf": round(hammer * 1.26, 0) if hammer else None,
                "currency": "USD",
                "lot_url": lot_url,
                "image_url": image_url,
            })
        except Exception as e:
            logger.debug(f"Invaluable DOM parse error: {e}")
            continue

    return results


async def search_reference(reference: str, limit: int = 30) -> list[dict]:
    """
    Cerca su Invaluable i risultati d'asta per una referenza orologio.
    Ritorna lista di dict normalizzati per il DB.
    """
    from playwright.async_api import async_playwright

    url = f"{BASE_URL}/search/?query={reference}&upcoming=false&resultsView=list"
    logger.info(f"Invaluable: ricerca referenza '{reference}' → {url}")
    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 800},
            )
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                # Tenta estrazione da __NEXT_DATA__
                next_data_raw = await page.evaluate(
                    "() => { try { return JSON.stringify(window.__NEXT_DATA__); } catch(e) { return null; } }"
                )
                if next_data_raw:
                    try:
                        next_data = json.loads(next_data_raw)
                        results = _extract_from_next_data(next_data, limit)
                        logger.info(f"Invaluable __NEXT_DATA__: {len(results)} lotti per '{reference}'")
                    except json.JSONDecodeError:
                        pass

                # Fallback DOM
                if not results:
                    html = await page.content()
                    results = _parse_dom_results(html, limit)
                    logger.info(f"Invaluable DOM fallback: {len(results)} lotti per '{reference}'")

                # Aggiungi la referenza cercata ai risultati
                for r in results:
                    if not r.get("reference"):
                        r["reference"] = reference

            except Exception as e:
                logger.error(f"Invaluable: errore pagina per '{reference}': {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Invaluable: errore Playwright per '{reference}': {e}")

    return results


async def get_upcoming_auctions(limit: int = 50) -> list[dict]:
    """
    Recupera le aste di orologi in arrivo da Invaluable.
    Ritorna lista di dict con info sull'asta (non normalizzati per il DB).
    """
    from playwright.async_api import async_playwright

    url = f"{BASE_URL}/search/?query=luxury+watches&upcoming=true&resultsView=list"
    logger.info(f"Invaluable: fetch upcoming auctions → {url}")
    upcoming = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 800},
            )
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                # Tenta __NEXT_DATA__
                next_data_raw = await page.evaluate(
                    "() => { try { return JSON.stringify(window.__NEXT_DATA__); } catch(e) { return null; } }"
                )
                if next_data_raw:
                    try:
                        next_data = json.loads(next_data_raw)
                        items = _extract_from_next_data(next_data, limit)
                        for item in items:
                            upcoming.append({
                                "house": item.get("auction_house", "Invaluable"),
                                "sale_name": item.get("sale_name", ""),
                                "location": item.get("sale_location", ""),
                                "date": item.get("sale_date", ""),
                                "url": item.get("lot_url", ""),
                                "catalog_url": item.get("lot_url", ""),
                                "highlights": [],
                                "source": "invaluable",
                            })
                    except json.JSONDecodeError:
                        pass

                # Fallback DOM
                if not upcoming:
                    html = await page.content()
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    for item in soup.select("div.auction-item, div.upcoming-auction, article.sale")[:limit]:
                        title_el = item.find("h2") or item.find("h3") or item.find(class_=re.compile(r"title"))
                        date_el = item.find(class_=re.compile(r"date"))
                        house_el = item.find(class_=re.compile(r"house|auctioneer"))
                        link_el = item.find("a")
                        upcoming.append({
                            "house": house_el.get_text(strip=True) if house_el else "Unknown",
                            "sale_name": title_el.get_text(strip=True) if title_el else "",
                            "location": "",
                            "date": date_el.get_text(strip=True) if date_el else "",
                            "url": link_el.get("href", "") if link_el else "",
                            "catalog_url": "",
                            "highlights": [],
                            "source": "invaluable",
                        })

                logger.info(f"Invaluable upcoming: {len(upcoming)} aste trovate")

            except Exception as e:
                logger.error(f"Invaluable: errore upcoming auctions: {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Invaluable: errore Playwright upcoming: {e}")

    return upcoming
