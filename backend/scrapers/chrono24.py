"""
Scraper reale per Chrono24.
Usa Playwright (browser headless) per bypassare Cloudflare.
Restituisce listing individuali con URL diretto all'annuncio.
"""
import re
import asyncio
import random
from datetime import datetime
from playwright.async_api import async_playwright, BrowserContext
from bs4 import BeautifulSoup
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing
from utils import scraping_api

logger = get_logger("scraper.chrono24")

_BASE = "https://www.chrono24.it"

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

CONDITION_MAP = {
    "nuovo": "new",
    "come nuovo": "mint",
    "eccellente": "mint",
    "buono": "good",
    "discreto": "fair",
    "new": "new",
    "mint": "mint",
    "excellent": "mint",
    "good": "good",
    "fair": "fair",
}


def _parse_price(text: str) -> float | None:
    text = text.replace('\xa0', '').replace(' ', '')
    match = re.search(r'([\d\.,]+)€', text)
    if not match:
        return None
    raw = match.group(1)
    # Formato europeo: 10.500,00 → 10500.00
    if ',' in raw and '.' in raw:
        raw = raw.replace('.', '').replace(',', '.')
    elif ',' in raw:
        raw = raw.replace(',', '.')
    elif '.' in raw and len(raw.split('.')[-1]) == 3:
        raw = raw.replace('.', '')  # separatore migliaia
    try:
        return float(raw)
    except ValueError:
        return None


def _parse_condition(text: str) -> str:
    text_lower = text.lower()
    for key, val in CONDITION_MAP.items():
        if key in text_lower:
            return val
    return "unknown"


async def _scrape_attempt(page, reference: str) -> tuple[list, int, str]:
    """Singolo tentativo di scraping. Ritorna (listings, status_code, preview)."""
    url = f"https://www.chrono24.it/search/index.htm?query={reference}&dosearch=1&resultview=list"
    await page.set_extra_http_headers({
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
    })
    resp = await page.goto(url, timeout=25000, wait_until="domcontentloaded")
    status = resp.status if resp else 0
    await page.wait_for_timeout(4000)

    raw_links = await page.evaluate("""
        () => Array.from(document.querySelectorAll('a[href*="--id"]'))
            .filter(a => a.innerText.includes('€'))
            .map(a => {
                const img = a.querySelector('img');
                let src = '';
                if (img) {
                    src = img.getAttribute('src') || img.getAttribute('data-src') || '';
                    if ((!src || src.startsWith('data:')) && img.getAttribute('srcset'))
                        src = img.getAttribute('srcset').split(',')[0].trim().split(' ')[0];
                }
                return { href: a.href, text: a.innerText.trim(), img: src };
            })
    """)

    listings = []
    seen = set()
    for item in raw_links:
        href = item["href"]
        if href in seen:
            continue
        seen.add(href)
        text = item["text"]
        price = _parse_price(text)
        if not price or price < 1500:
            continue
        if not is_watch_listing(text, "", price):
            continue
        lines = [l.strip() for l in text.split('\n') if l.strip() and '€' not in l and 'Vai alla' not in l and 'scheda' not in l and len(l.strip()) > 2]
        title = lines[0] if lines else reference
        description = lines[1] if len(lines) > 1 else ""
        country_match = re.search(r'\b([A-Z]{2})\b', text)
        location = country_match.group(1) if country_match else ""
        img = item.get("img") or ""
        listings.append(WatchListing(
            source="chrono24", reference=reference, price=price, currency="EUR",
            seller=title, url=href, condition=_parse_condition(text),
            scraped_at=datetime.now(), location=location, description=description or title,
            image_url=(img if img.startswith("http") else None),
        ))

    preview = (await page.content())[:200]
    return listings, status, preview


def _parse_html_listings(html: str, reference: str) -> list[WatchListing]:
    """Estrae i listing dall'HTML statico (percorso Scraping API). Stessa logica
    del percorso Playwright ma con BeautifulSoup."""
    soup = BeautifulSoup(html, "lxml")
    listings: list[WatchListing] = []
    seen: set[str] = set()
    for a in soup.select('a[href*="--id"]'):
        text = a.get_text("\n", strip=True)
        if "€" not in text:
            continue
        href = a.get("href") or ""
        if href.startswith("/"):
            href = _BASE + href
        if not href.startswith("http") or href in seen:
            continue
        seen.add(href)
        price = _parse_price(text)
        if not price or price < 1500:
            continue
        if not is_watch_listing(text, "", price):
            continue
        lines = [l.strip() for l in text.split('\n') if l.strip() and '€' not in l and 'Vai alla' not in l and 'scheda' not in l and len(l.strip()) > 2]
        title = lines[0] if lines else reference
        description = lines[1] if len(lines) > 1 else ""
        country_match = re.search(r'\b([A-Z]{2})\b', text)
        location = country_match.group(1) if country_match else ""
        img_el = a.find("img")
        img = ""
        if img_el:
            img = img_el.get("src") or img_el.get("data-src") or ""
            if (not img or img.startswith("data:")) and img_el.get("srcset"):
                img = img_el.get("srcset").split(",")[0].strip().split(" ")[0]
        listings.append(WatchListing(
            source="chrono24", reference=reference, price=price, currency="EUR",
            seller=title, url=href, condition=_parse_condition(text),
            scraped_at=datetime.now(), location=location, description=description or title,
            image_url=(img if img.startswith("http") else None),
        ))
    return listings


async def _scrape_via_api(reference: str) -> list[WatchListing]:
    """Percorso Scraping API: bypassa Cloudflare via proxy residenziale."""
    url = f"{_BASE}/search/index.htm?query={reference}&dosearch=1&resultview=list"
    html = await asyncio.to_thread(scraping_api.fetch_rendered_html, url)
    if not html:
        return []
    listings = _parse_html_listings(html, reference)
    logger.info(f"Chrono24 (Scraping API): {len(listings)} listing per {reference}")
    return listings


async def scrape(reference: str, context: BrowserContext) -> list[WatchListing]:
    # Se è configurata una Scraping API, usala: bypassa il blocco Cloudflare che
    # colpisce l'IP datacenter del server. Fallback a Playwright diretto se 0/errore.
    if scraping_api.is_enabled():
        try:
            api_listings = await _scrape_via_api(reference)
            if api_listings:
                return api_listings
            logger.warning("Chrono24: Scraping API 0 risultati — fallback a Playwright diretto")
        except Exception as e:
            logger.error(f"Chrono24 Scraping API error: {e}")

    page = await context.new_page()
    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    listings = []
    try:
        logger.info(f"Chrono24: scraping {reference}")
        for attempt in range(2):
            if attempt > 0:
                await asyncio.sleep(2)
                logger.debug(f"Chrono24 retry {attempt+1}/2 per {reference}")
            listings, status, preview = await _scrape_attempt(page, reference)
            if listings:
                break
            logger.warning(f"Chrono24: 0 risultati (tentativo {attempt+1}/2) | status={status} | preview={preview[:200]}")

        logger.info(f"Chrono24: {len(listings)} listing trovati per {reference}")
    except Exception as e:
        logger.error(f"Chrono24 scrape error: {e}")
    finally:
        await page.close()
    return listings


async def scrape_standalone(reference: str) -> list[WatchListing]:
    """Entry point standalone (per test senza agent)."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(_USER_AGENTS),
            locale="it-IT",
            timezone_id="Europe/Rome",
        )
        results = await scrape(reference, context)
        await browser.close()
        return results
