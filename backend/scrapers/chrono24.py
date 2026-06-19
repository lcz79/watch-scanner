"""
Scraper per Chrono24.
Via primaria: curl_cffi con impersonazione Chrome (bypassa Cloudflare senza proxy).
Fallback 1: Scraping API (ScraperAPI/ZenRows) se SCRAPER_API_KEY configurata.
Fallback 2: Playwright headless.
"""
import re
import asyncio
import random
from datetime import datetime
from playwright.async_api import BrowserContext
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
]

CONDITION_MAP = {
    "nuovo": "new", "come nuovo": "mint", "eccellente": "mint",
    "buono": "good", "discreto": "fair",
    "new": "new", "mint": "mint", "excellent": "mint",
    "good": "good", "fair": "fair",
}


def _parse_price(text: str) -> float | None:
    text = text.replace('\xa0', ' ')
    # Gestisce sia "10.990 €" che "14.500,00€" e "9.310,00 €"
    m = re.search(r'([\d][0-9\.,]*)\s*€', text)
    if not m:
        return None
    raw = m.group(1).strip()
    if ',' in raw and '.' in raw:
        raw = raw.replace('.', '').replace(',', '.')
    elif ',' in raw:
        raw = raw.replace(',', '.')
    elif '.' in raw and len(raw.split('.')[-1]) == 3:
        raw = raw.replace('.', '')
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


def _parse_html_listings(html: str, reference: str) -> list[WatchListing]:
    """Estrae listing dall'HTML (usato da tutti i percorsi)."""
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
        lines = [
            l.strip() for l in text.split('\n')
            if l.strip() and '€' not in l and len(l.strip()) > 2
        ]
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
            scraped_at=datetime.now(), location=location,
            description=description or title,
            image_url=(img if img.startswith("http") else None),
        ))
    return listings


async def _scrape_via_curl_cffi(reference: str) -> list[WatchListing]:
    """
    Via primaria: curl_cffi impersona Chrome a livello TLS (JA3/JA4 fingerprint).
    Bypassa Cloudflare Bot Management senza bisogno di proxy o scraping API.
    """
    try:
        from curl_cffi import requests as cr
    except ImportError:
        return []

    url = f"{_BASE}/search/index.htm?query={reference}&dosearch=1&resultview=list&pageSize=120"
    try:
        r = await asyncio.to_thread(
            cr.get, url,
            impersonate="chrome124",
            timeout=20,
            headers={
                "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
                "Referer": "https://www.google.it/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        if r.status_code != 200 or "Just a moment" in r.text or len(r.text) < 5000:
            logger.warning(f"Chrono24 curl_cffi: status={r.status_code} len={len(r.text)}")
            return []
        listings = _parse_html_listings(r.text, reference)
        logger.info(f"Chrono24 (curl_cffi): {len(listings)} listing per {reference}")
        return listings
    except Exception as e:
        logger.warning(f"Chrono24 curl_cffi error: {e}")
        return []


async def _scrape_via_api(reference: str) -> list[WatchListing]:
    """Fallback: Scraping API (ScraperAPI/ZenRows) se chiave configurata."""
    url = f"{_BASE}/search/index.htm?query={reference}&dosearch=1&resultview=list"
    html = await asyncio.to_thread(scraping_api.fetch_rendered_html, url)
    if not html:
        return []
    listings = _parse_html_listings(html, reference)
    logger.info(f"Chrono24 (Scraping API): {len(listings)} listing per {reference}")
    return listings


async def _scrape_via_playwright(reference: str, context: BrowserContext) -> list[WatchListing]:
    """Ultimo fallback: Playwright headless (bloccato su IP datacenter)."""
    page = await context.new_page()
    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    listings = []
    try:
        url = f"{_BASE}/search/index.htm?query={reference}&dosearch=1&resultview=list"
        await page.set_extra_http_headers({
            "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/",
        })
        resp = await page.goto(url, timeout=25000, wait_until="domcontentloaded")
        status = resp.status if resp else 0
        await page.wait_for_timeout(4000)
        html = await page.content()
        listings = _parse_html_listings(html, reference)
        if not listings:
            logger.warning(f"Chrono24 Playwright: 0 risultati (status={status})")
        logger.info(f"Chrono24 (Playwright): {len(listings)} listing per {reference}")
    except Exception as e:
        logger.error(f"Chrono24 Playwright error: {e}")
    finally:
        await page.close()
    return listings


async def scrape(reference: str, context: BrowserContext) -> list[WatchListing]:
    # 1. curl_cffi — Chrome TLS fingerprint, nessun proxy richiesto
    listings = await _scrape_via_curl_cffi(reference)
    if listings:
        return listings

    # 2. Scraping API (ScraperAPI/ZenRows) se SCRAPER_API_KEY configurata
    if scraping_api.is_enabled():
        try:
            listings = await _scrape_via_api(reference)
            if listings:
                return listings
            logger.warning("Chrono24: Scraping API 0 risultati — fallback Playwright")
        except Exception as e:
            logger.error(f"Chrono24 Scraping API error: {e}")

    # 3. Playwright diretto (bloccato su datacenter IP, ma funziona in locale)
    return await _scrape_via_playwright(reference, context)


async def scrape_standalone(reference: str) -> list[WatchListing]:
    """Entry point standalone per test."""
    # curl_cffi primo
    listings = await _scrape_via_curl_cffi(reference)
    if listings:
        return listings
    # Playwright fallback
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(_USER_AGENTS),
            locale="it-IT", timezone_id="Europe/Rome",
        )
        results = await _scrape_via_playwright(reference, context)
        await browser.close()
        return results
