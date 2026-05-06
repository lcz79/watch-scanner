"""
Scraper per Watchfinder.com.
Usa Playwright (browser headless) per navigare la ricerca e raccogliere listing.
Struttura identica a chrono24.py.
"""
import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, BrowserContext
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing

logger = get_logger("scraper.watchfinder")

_BASE_URL = "https://www.watchfinder.com/search"

CONDITION_MAP = {
    "unworn": "new",
    "mint": "mint",
    "excellent": "mint",
    "very good": "good",
    "good": "good",
    "fair": "fair",
    "pre-owned": "good",
    "new": "new",
}


def _parse_price(text: str) -> float | None:
    """
    Converte testi tipo "£12,500", "€12.500", "$12,500" in float.
    Watchfinder mostra prezzi in GBP / EUR a seconda della locale.
    """
    if not text:
        return None
    text = text.replace("\xa0", "").replace(" ", "").strip()
    # Rimuove simboli valuta
    text = re.sub(r"[£$€]", "", text).strip()
    # Formato anglosassone: 12,500.00 — virgola = migliaia, punto = decimali
    if re.search(r"\d,\d{3}", text):
        text = text.replace(",", "")
    # Formato europeo: 12.500,00
    elif re.search(r"\d\.\d{3},", text):
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(re.sub(r"[^\d.]", "", text))
    except (ValueError, TypeError):
        return None


def _parse_condition(text: str) -> str:
    text_lower = text.lower()
    for key, val in CONDITION_MAP.items():
        if key in text_lower:
            return val
    return "unknown"


async def scrape(reference: str, context: BrowserContext) -> list[WatchListing]:
    """
    Scrapa watchfinder.com per la referenza data.

    Args:
        reference: Referenza orologio, es. "116610LN"
        context: BrowserContext Playwright condiviso

    Returns:
        Lista di WatchListing trovati.
    """
    page = await context.new_page()
    await page.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    listings = []
    try:
        url = f"{_BASE_URL}?q={reference}"
        logger.info(f"Watchfinder: scraping {reference} → {url}")
        await page.goto(url, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)  # attendi hydration React

        # Watchfinder usa React: i card di listing vengono renderizzati
        # con classi variabili; cerchiamo pattern stabili nei link e nel DOM.
        raw_items = await page.evaluate("""
            () => {
                const results = [];
                // Card listing: link che porta alla pagina prodotto
                const cards = document.querySelectorAll('a[href*="/listing/"], a[href*="/watches/"]');
                cards.forEach(card => {
                    const href = card.href;
                    const text = card.innerText || '';
                    // Filtra link di navigazione senza prezzo
                    const hasPrice = /[£€$]\\s*[\\d,\\.]+/.test(text);
                    if (href && text && hasPrice) {
                        results.push({ href, text: text.trim() });
                    }
                });
                return results;
            }
        """)

        logger.info(f"Watchfinder: {len(raw_items)} card grezzi per {reference}")

        seen: set[str] = set()
        for item in raw_items:
            href: str = item["href"]
            # Normalizza URL (rimuovi querystring tracking)
            clean_href = href.split("?")[0]
            if clean_href in seen:
                continue
            seen.add(clean_href)

            text: str = item["text"]

            price = _parse_price(
                next(
                    (m.group(0) for m in [re.search(r'[£€$][\d,\.]+', text)] if m),
                    "",
                )
            )
            if not price or price < 1500:
                continue

            if not is_watch_listing(text, "", price):
                continue

            # Estrai righe informative escludendo prezzo e link interni
            lines = [
                ln.strip()
                for ln in text.split("\n")
                if ln.strip()
                and not re.search(r"[£€$]", ln)
                and len(ln.strip()) > 2
            ]

            title = lines[0] if lines else reference
            description = " · ".join(lines[1:3]) if len(lines) > 1 else title
            condition = _parse_condition(text)

            # Prova a estrarre location dal testo (es. "London, UK" o "UK")
            loc_match = re.search(
                r'\b(UK|United Kingdom|London|Manchester|Birmingham|Londra)\b',
                text,
                re.IGNORECASE,
            )
            location = loc_match.group(0) if loc_match else "UK"

            listings.append(
                WatchListing(
                    source="watchfinder",
                    reference=reference,
                    price=price,
                    currency="GBP",
                    seller="Watchfinder & Co.",
                    url=clean_href if clean_href.startswith("http") else f"https://www.watchfinder.com{clean_href}",
                    condition=condition,
                    scraped_at=datetime.now(),
                    location=location,
                    description=description or title,
                )
            )

        listings.sort(key=lambda x: x.price)
        logger.info(f"Watchfinder: {len(listings)} listing validi per {reference}")

    except Exception as e:
        logger.error(f"Watchfinder scrape error per '{reference}': {e}")
    finally:
        await page.close()

    return listings


async def scrape_standalone(reference: str) -> list[WatchListing]:
    """Entry point standalone (per test senza agent)."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-GB",
            timezone_id="Europe/London",
        )
        results = await scrape(reference, context)
        await browser.close()
        return results


if __name__ == "__main__":
    import sys

    ref = sys.argv[1] if len(sys.argv) > 1 else "116610LN"
    found = asyncio.run(scrape_standalone(ref))
    for l in found:
        print(f"{l.price} {l.currency} | {l.condition} | {l.url}")
