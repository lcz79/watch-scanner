"""
Scraper reale per eBay Italia.
Usa Playwright, filtra categoria Orologi da polso (31387).
"""
import re
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, BrowserContext
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing

logger = get_logger("scraper.ebay")

CONDITION_MAP = {
    "nuovo": "new",
    "usato": "good",
    "ricondizionato": "fair",
    "non specificato": "unknown",
}

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


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


async def _scrape_attempt(reference: str, context: BrowserContext) -> tuple[list[WatchListing], int, str]:
    """
    Singolo tentativo di scraping. Ritorna (listings, status_code, response_preview).
    status_code è -1 se non recuperato (es. timeout/errore di rete).
    """
    page = await context.new_page()

    await page.set_extra_http_headers({
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
    })

    listings = []
    status_code = -1
    response_preview = ""

    try:
        url = f"https://www.ebay.it/sch/31387/i.html?_nkw={reference}&_sop=15&_ipg=60&LH_BIN=1"

        response = await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        if response:
            status_code = response.status
            if status_code != 200:
                try:
                    body = await response.text()
                    response_preview = body[:200]
                except Exception:
                    response_preview = "(body non leggibile)"
                return listings, status_code, response_preview

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
                    const imgEl = li.querySelector('img.s-item__image-img, img[src*="thumbs"], img[src*="i.ebayimg"]');
                    return {
                        url: a ? a.href.split('?')[0] : '',
                        price_text: priceEl ? priceEl.innerText.trim() : '',
                        title: titleEl ? titleEl.innerText.trim().slice(0, 100) : '',
                        seller: sellerEl ? sellerEl.innerText.trim().split('(')[0].trim() : 'Venditore eBay',
                        condition: condEl ? condEl.innerText.trim().toLowerCase() : '',
                        location: locEl ? locEl.innerText.trim() : 'Italia',
                        image: imgEl ? (imgEl.src || imgEl.dataset.src || null) : null,
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
                image_url=item.get("image") or None,
            ))

        listings.sort(key=lambda x: x.price)

    except Exception as e:
        logger.error(f"eBay attempt error: {e}")
    finally:
        await page.close()

    return listings, status_code, response_preview


async def scrape(reference: str, context: BrowserContext) -> list[WatchListing]:
    logger.info(f"eBay: scraping {reference}")

    max_attempts = 3
    last_status = -1
    last_preview = ""

    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            logger.info(f"eBay: tentativo {attempt}/{max_attempts} per {reference} (delay 3s)")
            await asyncio.sleep(3)

        listings, status_code, response_preview = await _scrape_attempt(reference, context)
        last_status = status_code
        last_preview = response_preview

        if status_code not in (-1, 200):
            logger.warning(
                f"eBay: tentativo {attempt} status {status_code} | preview: {response_preview!r}"
            )
            continue

        if listings:
            logger.info(f"eBay: {len(listings)} listing validi per {reference} (tentativo {attempt})")
            return listings

        logger.debug(f"eBay: tentativo {attempt} — 0 risultati per {reference}")

    logger.warning(
        f"eBay: 0 risultati dopo {max_attempts} tentativi per {reference} | "
        f"ultimo status={last_status} | preview={last_preview!r}"
    )
    return []


async def scrape_standalone(reference: str) -> list[WatchListing]:
    """Entry point standalone (per test senza agent)."""
    from playwright.async_api import async_playwright
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
