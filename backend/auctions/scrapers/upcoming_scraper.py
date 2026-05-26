"""
Upcoming auctions scraper — calendari aste principali case.
Usa Playwright per gestire JS rendering e redirect.

Targets:
- Phillips:   https://www.phillipswatches.com/auctions/
- Christie's:  https://www.christies.com/en/calendar
- Sotheby's:  https://www.sothebys.com/en/calendar
- Antiquorum:  https://www.antiquorum.swiss/en/upcoming-auctions
"""
import asyncio
import re
from datetime import datetime

from utils.logger import get_logger

logger = get_logger("auctions")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


def _parse_date_string(text: str) -> str:
    """Tenta di parsare una stringa data in formato ISO YYYY-MM-DD."""
    if not text:
        return ""
    text = text.strip()

    # Già in formato ISO
    if re.match(r"\d{4}-\d{2}-\d{2}", text):
        return text[:10]

    # Formato "10 May 2026" o "May 10, 2026"
    patterns = [
        r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",   # "10 May 2026"
        r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})",  # "May 10, 2026"
        r"(\d{1,2})/(\d{1,2})/(\d{4})",           # "05/10/2026"
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            try:
                g = m.groups()
                if re.match(r"[A-Za-z]", g[0]):
                    month = MONTH_MAP.get(g[0].lower(), "01")
                    day = g[1].zfill(2)
                    year = g[2]
                else:
                    day = g[0].zfill(2)
                    month_str = g[1]
                    year = g[2]
                    if re.match(r"[A-Za-z]", month_str):
                        month = MONTH_MAP.get(month_str.lower(), "01")
                    else:
                        month = month_str.zfill(2)
                return f"{year}-{month}-{day}"
            except Exception:
                pass

    return ""


async def _new_page(playwright_browser):
    """Crea un nuovo page context con user agent realistico."""
    context = await playwright_browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1280, "height": 900},
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
    )
    return await context.new_page(), context


# ---------------------------------------------------------------------------
# Phillips
# ---------------------------------------------------------------------------

async def scrape_phillips_upcoming() -> list[dict]:
    """Scrape le aste future da phillipswatches.com."""
    from playwright.async_api import async_playwright

    url = "https://www.phillipswatches.com/auctions/"
    logger.info(f"Phillips upcoming: {url}")
    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page, context = await _new_page(browser)
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                from bs4 import BeautifulSoup
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Cerca sezioni auction/sale
                auction_items = soup.select(
                    "article.auction, div.auction-item, div.sale-item, "
                    "li.auction, div[class*='auction'], a[href*='/auction/'], "
                    "a[href*='/auctions/']"
                )

                # Fallback: cerca link che sembrano aste future
                if not auction_items:
                    auction_items = [
                        a for a in soup.find_all("a", href=True)
                        if re.search(r"/auction/|/auctions/|/sale/", a.get("href", ""))
                        and "results" not in a.get("href", "").lower()
                    ]

                seen_urls = set()
                for item in auction_items[:30]:
                    try:
                        href = item.get("href", "") if item.name == "a" else ""
                        if not href:
                            link = item.find("a", href=True)
                            href = link.get("href", "") if link else ""

                        if not href:
                            continue
                        full_url = href if href.startswith("http") else f"https://www.phillipswatches.com{href}"
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)

                        # Titolo
                        title_el = item.find(class_=re.compile(r"title|name|heading")) or item.find("h2") or item.find("h3")
                        sale_name = title_el.get_text(strip=True) if title_el else item.get_text(strip=True)[:80]

                        # Data
                        date_el = item.find(class_=re.compile(r"date|time|when"))
                        date_str = _parse_date_string(date_el.get_text() if date_el else "")

                        # Location
                        loc_el = item.find(class_=re.compile(r"location|place|city|venue"))
                        location = loc_el.get_text(strip=True) if loc_el else "Geneva"

                        if sale_name and len(sale_name) > 3:
                            results.append({
                                "house": "Phillips",
                                "sale_name": sale_name,
                                "location": location,
                                "date": date_str,
                                "url": full_url,
                                "catalog_url": full_url,
                                "highlights": [],
                                "source": "phillips_live",
                            })
                    except Exception as e:
                        logger.debug(f"Phillips upcoming item error: {e}")

                logger.info(f"Phillips upcoming: {len(results)} aste trovate")

            except Exception as e:
                logger.error(f"Phillips upcoming scrape error: {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Phillips upcoming Playwright error: {e}")

    return results


# ---------------------------------------------------------------------------
# Christie's
# ---------------------------------------------------------------------------

async def scrape_christies_upcoming() -> list[dict]:
    """Scrape le aste future da christies.com."""
    from playwright.async_api import async_playwright

    url = "https://www.christies.com/en/calendar"
    logger.info(f"Christie's upcoming: {url}")
    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page, context = await _new_page(browser)
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                from bs4 import BeautifulSoup
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Christie's usa data-testid e classi specifiche
                sale_items = soup.select(
                    "[data-testid*='sale'], [data-testid*='auction'], "
                    "div.card-sale, article.sale, li.calendar-item, "
                    "div[class*='SaleCard'], div[class*='sale-card']"
                )

                if not sale_items:
                    # Cerca link che contengono watches o timepieces
                    sale_items = [
                        a for a in soup.find_all("a", href=True)
                        if re.search(r"/watch|timepiece|horolog", a.get("href", "") + a.get_text(), re.I)
                    ]

                seen_urls = set()
                for item in sale_items[:40]:
                    try:
                        href = item.get("href", "") if item.name == "a" else ""
                        if not href:
                            link = item.find("a", href=True)
                            href = link.get("href", "") if link else ""

                        full_url = href if href.startswith("http") else f"https://www.christies.com{href}"
                        if full_url in seen_urls or not href:
                            continue
                        seen_urls.add(full_url)

                        title_el = (
                            item.find(class_=re.compile(r"title|name|heading", re.I))
                            or item.find("h2") or item.find("h3") or item.find("h4")
                        )
                        sale_name = title_el.get_text(strip=True) if title_el else item.get_text(strip=True)[:100]

                        date_el = item.find(class_=re.compile(r"date|time", re.I)) or item.find("time")
                        date_text = date_el.get("datetime", date_el.get_text()) if date_el else ""
                        date_str = _parse_date_string(str(date_text))

                        loc_el = item.find(class_=re.compile(r"location|place|city", re.I))
                        location = loc_el.get_text(strip=True) if loc_el else ""

                        if sale_name and len(sale_name) > 3:
                            results.append({
                                "house": "Christie's",
                                "sale_name": sale_name,
                                "location": location,
                                "date": date_str,
                                "url": full_url,
                                "catalog_url": full_url,
                                "highlights": [],
                                "source": "christies_live",
                            })
                    except Exception as e:
                        logger.debug(f"Christie's item error: {e}")

                logger.info(f"Christie's upcoming: {len(results)} aste trovate")

            except Exception as e:
                logger.error(f"Christie's upcoming scrape error: {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Christie's upcoming Playwright error: {e}")

    return results


# ---------------------------------------------------------------------------
# Sotheby's
# ---------------------------------------------------------------------------

async def scrape_sothebys_upcoming() -> list[dict]:
    """Scrape le aste future da sothebys.com."""
    from playwright.async_api import async_playwright

    url = "https://www.sothebys.com/en/calendar"
    logger.info(f"Sotheby's upcoming: {url}")
    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page, context = await _new_page(browser)
            try:
                await page.goto(url, wait_until="networkidle", timeout=35000)
                await asyncio.sleep(3)

                from bs4 import BeautifulSoup
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Sotheby's usa componenti React con classi lunghe
                sale_items = soup.select(
                    "div[class*='AuctionCard'], div[class*='auction-card'], "
                    "article[class*='auction'], li[class*='sale'], "
                    "div[class*='SaleRow'], a[href*='/en/buy/auction/']"
                )

                if not sale_items:
                    sale_items = [
                        a for a in soup.find_all("a", href=True)
                        if "/en/buy/auction/" in a.get("href", "")
                        or "/en/calendar/" in a.get("href", "")
                    ]

                seen_urls = set()
                for item in sale_items[:40]:
                    try:
                        href = item.get("href", "") if item.name == "a" else ""
                        if not href:
                            link = item.find("a", href=True)
                            href = link.get("href", "") if link else ""

                        full_url = href if href.startswith("http") else f"https://www.sothebys.com{href}"
                        if full_url in seen_urls or not href:
                            continue
                        seen_urls.add(full_url)

                        title_el = (
                            item.find("h2") or item.find("h3") or item.find("h4")
                            or item.find(class_=re.compile(r"title|name", re.I))
                        )
                        sale_name = title_el.get_text(strip=True) if title_el else item.get_text(strip=True)[:100]

                        date_el = item.find("time") or item.find(class_=re.compile(r"date|time", re.I))
                        date_text = date_el.get("datetime", date_el.get_text()) if date_el else ""
                        date_str = _parse_date_string(str(date_text))

                        loc_el = item.find(class_=re.compile(r"location|place|city|venue", re.I))
                        location = loc_el.get_text(strip=True) if loc_el else ""

                        if sale_name and len(sale_name) > 3:
                            results.append({
                                "house": "Sotheby's",
                                "sale_name": sale_name,
                                "location": location,
                                "date": date_str,
                                "url": full_url,
                                "catalog_url": full_url,
                                "highlights": [],
                                "source": "sothebys_live",
                            })
                    except Exception as e:
                        logger.debug(f"Sotheby's item error: {e}")

                logger.info(f"Sotheby's upcoming: {len(results)} aste trovate")

            except Exception as e:
                logger.error(f"Sotheby's upcoming scrape error: {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Sotheby's upcoming Playwright error: {e}")

    return results


# ---------------------------------------------------------------------------
# Antiquorum
# ---------------------------------------------------------------------------

async def scrape_antiquorum_upcoming() -> list[dict]:
    """Scrape le aste future da antiquorum.swiss."""
    from playwright.async_api import async_playwright

    url = "https://www.antiquorum.swiss/en/upcoming-auctions"
    logger.info(f"Antiquorum upcoming: {url}")
    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page, context = await _new_page(browser)
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                from bs4 import BeautifulSoup
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                sale_items = soup.select(
                    "div.auction-item, article.auction, div.sale, "
                    "li.auction-list-item, div[class*='auction']"
                )

                if not sale_items:
                    sale_items = [
                        a for a in soup.find_all("a", href=True)
                        if re.search(r"/auction|/sale|/upcoming", a.get("href", ""), re.I)
                    ]

                seen_urls = set()
                for item in sale_items[:20]:
                    try:
                        href = item.get("href", "") if item.name == "a" else ""
                        if not href:
                            link = item.find("a", href=True)
                            href = link.get("href", "") if link else ""

                        full_url = href if href.startswith("http") else f"https://www.antiquorum.swiss{href}"
                        if full_url in seen_urls or not href:
                            continue
                        seen_urls.add(full_url)

                        title_el = (
                            item.find("h2") or item.find("h3") or item.find("h1")
                            or item.find(class_=re.compile(r"title|name", re.I))
                        )
                        sale_name = title_el.get_text(strip=True) if title_el else item.get_text(strip=True)[:100]

                        date_el = item.find(class_=re.compile(r"date|time|when", re.I)) or item.find("time")
                        date_text = date_el.get("datetime", date_el.get_text()) if date_el else ""
                        date_str = _parse_date_string(str(date_text))

                        loc_el = item.find(class_=re.compile(r"location|place|city", re.I))
                        location = loc_el.get_text(strip=True) if loc_el else "Geneva"

                        if sale_name and len(sale_name) > 3:
                            results.append({
                                "house": "Antiquorum",
                                "sale_name": sale_name,
                                "location": location,
                                "date": date_str,
                                "url": full_url,
                                "catalog_url": full_url,
                                "highlights": [],
                                "source": "antiquorum_live",
                            })
                    except Exception as e:
                        logger.debug(f"Antiquorum item error: {e}")

                logger.info(f"Antiquorum upcoming: {len(results)} aste trovate")

            except Exception as e:
                logger.error(f"Antiquorum upcoming scrape error: {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Antiquorum upcoming Playwright error: {e}")

    return results


# ---------------------------------------------------------------------------
# Aggregatore
# ---------------------------------------------------------------------------

async def scrape_all_upcoming() -> list[dict]:
    """
    Scrape upcoming auctions da tutte le case d'aste in parallelo.
    Ritorna lista unificata ordinata per data.
    """
    logger.info("Upcoming scraper: avvio scraping parallelo di tutte le case")

    tasks = [
        scrape_phillips_upcoming(),
        scrape_christies_upcoming(),
        scrape_sothebys_upcoming(),
        scrape_antiquorum_upcoming(),
    ]

    # Esegui in parallelo con timeout totale
    results_list = await asyncio.gather(*tasks, return_exceptions=True)

    all_results = []
    for res in results_list:
        if isinstance(res, Exception):
            logger.error(f"Upcoming scraper task error: {res}")
        elif isinstance(res, list):
            all_results.extend(res)

    # Dedup per (house, sale_name)
    seen = set()
    deduped = []
    for r in all_results:
        key = (r.get("house", ""), r.get("sale_name", ""))
        if key not in seen and key[1]:
            seen.add(key)
            deduped.append(r)

    # Ordina per data
    def _sort_key(x):
        d = x.get("date", "")
        return d if d else "9999-99-99"

    deduped.sort(key=_sort_key)

    logger.info(f"Upcoming scraper: totale {len(deduped)} aste uniche trovate")
    return deduped
