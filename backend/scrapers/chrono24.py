"""
Scraper reale per Chrono24.
Usa Playwright (browser headless) per bypassare Cloudflare.
Restituisce listing individuali con URL diretto all'annuncio.
"""
import re
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, BrowserContext
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing

logger = get_logger("scraper.chrono24")

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

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


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


async def _scrape_attempt(reference: str, context: BrowserContext) -> tuple[list[WatchListing], int, str]:
    """
    Singolo tentativo di scraping. Ritorna (listings, status_code, response_preview).
    status_code è -1 se non recuperato (es. timeout/errore di rete).
    """
    page = await context.new_page()

    # Extra headers per sembrare traffico organico
    await page.set_extra_http_headers({
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
    })
    await page.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    listings = []
    status_code = -1
    response_preview = ""

    try:
        url = f"https://www.chrono24.it/search/index.htm?query={reference}&dosearch=1&resultview=list"

        response = await page.goto(url, timeout=40000, wait_until="domcontentloaded")
        if response:
            status_code = response.status
            if status_code != 200:
                try:
                    body = await response.text()
                    response_preview = body[:200]
                except Exception:
                    response_preview = "(body non leggibile)"
                return listings, status_code, response_preview

        await page.wait_for_timeout(8000)  # JS listing cards need time to render

        # Estrai tutti i link di listing con il loro testo (che include prezzo) e immagine
        raw_links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href*="--id"]'))
                .filter(a => a.innerText.includes('€'))
                .map(a => ({
                    href: a.href,
                    text: a.innerText.trim(),
                    image: a.querySelector('img')?.src
                        || a.querySelector('img')?.dataset.src
                        || a.closest('article,div[class*="article"],div[class*="card"]')?.querySelector('img')?.src
                        || a.closest('article,div[class*="article"],div[class*="card"]')?.querySelector('img')?.dataset.src
                        || null
                }))
        """)

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

            # Estrai righe informative (rimuovi navigazione e prezzo)
            lines = [
                l.strip() for l in text.split('\n')
                if l.strip()
                and '€' not in l
                and 'Vai alla' not in l
                and 'scheda' not in l
                and len(l.strip()) > 2
            ]

            # Prima riga utile = titolo/referenza, seconda = descrizione aggiuntiva
            title = lines[0] if lines else reference
            description = lines[1] if len(lines) > 1 else ""

            # Paese venditore (2 lettere uppercase isolate)
            country_match = re.search(r'\b([A-Z]{2})\b', text)
            location = country_match.group(1) if country_match else ""

            condition = _parse_condition(text)

            listings.append(WatchListing(
                source="chrono24",
                reference=reference,
                price=price,
                currency="EUR",
                seller=title,
                url=href,
                condition=condition,
                scraped_at=datetime.now(),
                location=location,
                description=description or title,
                image_url=item.get("image") or None,
            ))

    except Exception as e:
        logger.error(f"Chrono24 attempt error: {e}")
    finally:
        await page.close()

    return listings, status_code, response_preview


async def scrape(reference: str, context: BrowserContext) -> list[WatchListing]:
    logger.info(f"Chrono24: scraping {reference}")

    max_attempts = 3
    last_status = -1
    last_preview = ""

    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            logger.info(f"Chrono24: tentativo {attempt}/{max_attempts} per {reference} (delay 3s)")
            await asyncio.sleep(3)

        listings, status_code, response_preview = await _scrape_attempt(reference, context)
        last_status = status_code
        last_preview = response_preview

        if status_code not in (-1, 200):
            logger.warning(
                f"Chrono24: tentativo {attempt} status {status_code} | preview: {response_preview!r}"
            )
            continue

        if listings:
            logger.info(f"Chrono24: {len(listings)} listing trovati per {reference} (tentativo {attempt})")
            return listings

        logger.debug(f"Chrono24: tentativo {attempt} — 0 risultati per {reference}")

    logger.warning(
        f"Chrono24: 0 risultati dopo {max_attempts} tentativi per {reference} | "
        f"ultimo status={last_status} | preview={last_preview!r}"
    )
    return []


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
