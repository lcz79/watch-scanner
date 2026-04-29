"""
Scraper reale per eBay Italia.
Usa Playwright, filtra categoria Orologi da polso (31387).
"""
import re
from datetime import datetime
from playwright.async_api import BrowserContext
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


async def scrape(reference: str, context: BrowserContext) -> list[WatchListing]:
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
                    return {
                        url: a ? a.href.split('?')[0] : '',
                        price_text: priceEl ? priceEl.innerText.trim() : '',
                        title: titleEl ? titleEl.innerText.trim().slice(0, 100) : '',
                        seller: sellerEl ? sellerEl.innerText.trim().split('(')[0].trim() : 'Venditore eBay',
                        condition: condEl ? condEl.innerText.trim().toLowerCase() : '',
                        location: locEl ? locEl.innerText.trim() : 'Italia',
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
            ))

        listings.sort(key=lambda x: x.price)
        logger.info(f"eBay: {len(listings)} listing validi per {reference}")
    except Exception as e:
        logger.error(f"eBay scrape error: {e}")
    finally:
        await page.close()

    return listings
