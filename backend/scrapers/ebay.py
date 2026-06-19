"""
Scraper reale per eBay Italia.
Usa Playwright, filtra categoria Orologi da polso (31387).
"""
import re
import asyncio
from datetime import datetime
from playwright.async_api import BrowserContext
from bs4 import BeautifulSoup
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing
from utils import scraping_api

logger = get_logger("scraper.ebay")

CONDITION_MAP = {
    "nuovo": "new",
    "usato": "good",
    "ricondizionato": "fair",
    "non specificato": "unknown",
}


def _parse_price(text: str) -> float | None:
    # Gestisce "EUR 9.310,00" o "9.310,00 EUR" o range "9.000,00 a 10.000,00"
    text = text.split(" a ")[0]  # prende il minore nei range
    nums = re.findall(r'[\d\.]+,\d{2}', text)
    if not nums:
        return None
    try:
        return float(nums[0].replace('.', '').replace(',', '.'))
    except ValueError:
        return None


def _img_from(el) -> str | None:
    if not el:
        return None
    img = el.get("src") or el.get("data-src") or ""
    if (not img or img.startswith("data:")) and el.get("srcset"):
        img = el.get("srcset").split(",")[0].strip().split(" ")[0]
    return img if img.startswith("http") else None


def _parse_html_listings(html: str, reference: str) -> list[WatchListing]:
    """Estrae i listing dall'HTML statico (percorso Scraping API)."""
    soup = BeautifulSoup(html, "lxml")
    listings: list[WatchListing] = []
    for li in soup.select(".srp-river-results li"):
        a = li.select_one('a[href*="/itm/"]')
        if not a:
            continue
        url = (a.get("href") or "").split("?")[0]
        if not url or "/itm/123456" in url:
            continue
        price_el = li.select_one('.s-item__price, [class*="price"]')
        title_el = li.select_one('.s-item__title, [class*="title"], h3')
        cond_el = li.select_one('.SECONDARY_INFO, [class*="condition"]')
        loc_el = li.select_one('[class*="location"], [class*="country"]')
        price_text = price_el.get_text(strip=True) if price_el else ""
        title = (title_el.get_text(strip=True)[:100] if title_el else "")
        price = _parse_price(price_text)
        if not price or price < 1500:
            continue
        if not is_watch_listing(title, "", price):
            continue
        cond_text = cond_el.get_text(strip=True).lower() if cond_el else ""
        condition = next((v for k, v in CONDITION_MAP.items() if k in cond_text), "unknown")
        listings.append(WatchListing(
            source="ebay", reference=reference, price=price, currency="EUR",
            seller="Venditore eBay", url=url, condition=condition,
            scraped_at=datetime.now(),
            location=(loc_el.get_text(strip=True) if loc_el else "Italia"),
            description=title,
            image_url=_img_from(li.select_one('.s-item__image img, img')),
        ))
    listings.sort(key=lambda x: x.price)
    return listings


async def _scrape_via_httpx(reference: str) -> list[WatchListing]:
    """
    Via primaria: httpx diretto. eBay non usa Cloudflare Bot Management aggressivo
    come Chrono24 — una semplice richiesta HTTP con UA realistico funziona.
    """
    import httpx
    url = f"https://www.ebay.it/sch/31387/i.html?_nkw={reference}&_sop=15&_ipg=60&LH_BIN=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.it/",
    }
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
            r = await client.get(url)
            if r.status_code != 200 or len(r.text) < 10000:
                logger.warning(f"eBay httpx: status={r.status_code}")
                return []
            listings = _parse_html_listings(r.text, reference)
            logger.info(f"eBay (httpx): {len(listings)} listing per {reference}")
            return listings
    except Exception as e:
        logger.warning(f"eBay httpx error: {e}")
        return []


async def _scrape_via_api(reference: str) -> list[WatchListing]:
    url = f"https://www.ebay.it/sch/31387/i.html?_nkw={reference}&_sop=15&_ipg=60&LH_BIN=1"
    html = await asyncio.to_thread(scraping_api.fetch_rendered_html, url)
    if not html:
        return []
    listings = _parse_html_listings(html, reference)
    logger.info(f"eBay (Scraping API): {len(listings)} listing per {reference}")
    return listings


async def scrape(reference: str, context: BrowserContext) -> list[WatchListing]:
    # 1. httpx diretto — eBay non blocca gli IP datacenter come Chrono24
    listings = await _scrape_via_httpx(reference)
    if listings:
        return listings

    # 2. Scraping API se configurata
    if scraping_api.is_enabled():
        try:
            listings = await _scrape_via_api(reference)
            if listings:
                return listings
            logger.warning("eBay: Scraping API 0 risultati — fallback a Playwright diretto")
        except Exception as e:
            logger.error(f"eBay Scraping API error: {e}")

    page = await context.new_page()
    listings = []
    try:
        url = f"https://www.ebay.it/sch/31387/i.html?_nkw={reference}&_sop=15&_ipg=60&LH_BIN=1"
        logger.info(f"eBay: scraping {reference}")
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        items = await page.evaluate("""
            () => Array.from(document.querySelectorAll('.srp-river-results li'))
                .filter(li => {
                    const a = li.querySelector('a[href*="/itm/"]');
                    return a && !a.href.includes('/itm/123456');
                })
                .map(li => {
                    const a = li.querySelector('a[href*="/itm/"]');
                    const priceEl = li.querySelector('.s-item__price, [class*="price"]');
                    const titleEl = li.querySelector('[class*="title"], h3');
                    const sellerEl = li.querySelector('[class*="seller"]');
                    const condEl = li.querySelector('.SECONDARY_INFO, [class*="condition"]');
                    const locEl = li.querySelector('[class*="location"], [class*="country"]');
                    const imgEl = li.querySelector('.s-item__image img, img');
                    let img = '';
                    if (imgEl) {
                        img = imgEl.getAttribute('src') || imgEl.getAttribute('data-src') || '';
                        if ((!img || img.startsWith('data:')) && imgEl.getAttribute('srcset'))
                            img = imgEl.getAttribute('srcset').split(',')[0].trim().split(' ')[0];
                    }
                    return {
                        url: a ? a.href.split('?')[0] : '',
                        price_text: priceEl ? priceEl.innerText.trim() : '',
                        title: titleEl ? titleEl.innerText.trim().slice(0, 100) : '',
                        seller: sellerEl ? sellerEl.innerText.trim().split('(')[0].trim() : 'Venditore eBay',
                        condition: condEl ? condEl.innerText.trim().toLowerCase() : '',
                        location: locEl ? locEl.innerText.trim() : 'Italia',
                        image: img,
                    }
                })
        """)

        logger.info(f"eBay: {len(items)} item raw")

        for item in items:
            if not item["url"] or not item["price_text"]:
                continue
            price = _parse_price(item["price_text"])
            if not price or price < 1500:
                continue
            # Filtra accessori/parti di ricambio
            if not is_watch_listing(item["title"], "", price):
                continue

            condition = next(
                (v for k, v in CONDITION_MAP.items() if k in item["condition"]),
                "unknown"
            )

            listings.append(WatchListing(
                source="ebay",
                reference=reference,
                price=price,
                currency="EUR",
                seller=item["seller"] or "Venditore eBay",
                url=item["url"],
                condition=condition,
                scraped_at=datetime.now(),
                location=item.get("location", "Italia"),
                description=item["title"],
                image_url=(item.get("image") if str(item.get("image", "")).startswith("http") else None),
            ))

        listings.sort(key=lambda x: x.price)
        logger.info(f"eBay: {len(listings)} listing validi per {reference}")
    except Exception as e:
        logger.error(f"eBay scrape error: {e}")
    finally:
        await page.close()

    return listings
