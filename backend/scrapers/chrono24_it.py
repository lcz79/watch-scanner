"""
Scraper per Chrono24.it — versione italiana con filtro venditori italiani.
Variante di chrono24.py ottimizzata per:
- URL italiano (chrono24.it)
- Filtrare annunci con location IT / Italia
- Parsing prezzi in formato europeo italiano
"""
import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, BrowserContext
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing

logger = get_logger("scraper.chrono24_it")

_SEARCH_URL = "https://www.chrono24.it/search/index.htm"

# Token che identificano venditori italiani nel testo della card
_IT_LOCATION_TOKENS = {
    "it", "italia", "italy", "milan", "milano", "roma", "rome",
    "torino", "turin", "napoli", "naples", "firenze", "florence",
    "bologna", "venezia", "venice", "genova", "genoa", "palermo",
    "bari", "catania", "verona", "trieste", "brescia", "padova",
    "bergamo", "modena", "parma", "reggio", "livorno", "rimini",
    "cagliari", "pescara", "taranto", "messina", "prato", "ferrara",
}

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
    "unworn": "new",
}


def _parse_price_it(text: str) -> float | None:
    """
    Parsing prezzi formato italiano: 10.500,00 € oppure € 10.500.
    Gestisce anche formati misti e spazi non-breaking.
    """
    if not text:
        return None
    text = text.replace("\xa0", "").replace(" ", "").replace(" ", "")

    # Cerca pattern con € davanti o dietro
    m = re.search(r"([\d\.,]+)\s*€", text) or re.search(r"€\s*([\d\.,]+)", text)
    if not m:
        return None

    raw = m.group(1)

    # Formato italiano standard: 10.500,00
    if "," in raw and "." in raw:
        # Virgola = decimali, punto = migliaia
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        # Solo virgola: potrebbe essere decimale (10,50) o migliaia (10,500)
        parts = raw.split(",")
        if len(parts) == 2 and len(parts[1]) == 3:
            # Es: "10,500" → migliaia anglosassone (poco probabile su .it, ma gestito)
            raw = raw.replace(",", "")
        else:
            raw = raw.replace(",", ".")
    elif "." in raw:
        # Solo punto: migliaia se la parte dopo è esattamente 3 cifre
        parts = raw.split(".")
        if len(parts) == 2 and len(parts[1]) == 3:
            raw = raw.replace(".", "")  # separatore migliaia
        # altrimenti punto decimale anglosassone, lascia invariato

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


def _is_italian_seller(text: str) -> bool:
    """
    Controlla se il testo della card indica un venditore italiano.
    Chrono24 mostra il paese in sigla (IT) o per esteso nel testo del card.
    """
    text_lower = text.lower()
    # Sigla ISO 2 lettere isolata (es. " IT " o "(IT)")
    if re.search(r'(?<![A-Z])IT(?![A-Z])', text):
        return True
    # Nomi di città/paese italiani
    tokens = re.split(r'[\s,\n\|•]+', text_lower)
    return any(tok in _IT_LOCATION_TOKENS for tok in tokens)


async def scrape(reference: str, context: BrowserContext) -> list[WatchListing]:
    """
    Scrapa Chrono24.it filtrando solo venditori italiani.

    Args:
        reference: Referenza orologio, es. "116610LN"
        context: BrowserContext Playwright condiviso

    Returns:
        Lista di WatchListing di venditori italiani.
    """
    page = await context.new_page()
    await page.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    listings = []
    try:
        url = (
            f"{_SEARCH_URL}"
            f"?query={reference}"
            f"&dosearch=1"
            f"&resultview=list"
            f"&watchTypes=U"   # usato (pre-owned)
        )
        logger.info(f"Chrono24 IT: scraping {reference}")
        await page.goto(url, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)  # attendi rendering JS

        raw_links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href*="--id"]'))
                .filter(a => a.innerText.includes('€'))
                .map(a => ({
                    href: a.href,
                    text: a.innerText.trim()
                }))
        """)

        logger.info(f"Chrono24 IT: {len(raw_links)} link grezzi per {reference}")

        seen: set[str] = set()
        italian_count = 0

        for item in raw_links:
            href: str = item["href"]
            if href in seen:
                continue
            seen.add(href)

            text: str = item["text"]

            # Filtra subito i non-italiani per risparmiare CPU
            if not _is_italian_seller(text):
                continue
            italian_count += 1

            price = _parse_price_it(text)
            if not price or price < 1500:
                continue

            if not is_watch_listing(text, "", price):
                continue

            # Righe informative (no prezzo, no navigazione)
            lines = [
                ln.strip()
                for ln in text.split("\n")
                if ln.strip()
                and "€" not in ln
                and "Vai alla" not in ln
                and "scheda" not in ln
                and len(ln.strip()) > 2
            ]

            title = lines[0] if lines else reference
            description = lines[1] if len(lines) > 1 else ""

            # Estrai location (preferisce il token italiano trovato)
            location = "Italia"
            for ln in lines:
                ln_lower = ln.lower().strip()
                if ln_lower in _IT_LOCATION_TOKENS:
                    location = ln.strip().capitalize()
                    break
            # Fallback: cerca sigla IT nel testo originale
            if location == "Italia":
                loc_m = re.search(r'\b([A-Z]{2})\b', text)
                if loc_m:
                    location = loc_m.group(1)

            condition = _parse_condition(text)

            listings.append(
                WatchListing(
                    source="chrono24_it",
                    reference=reference,
                    price=price,
                    currency="EUR",
                    seller=title,
                    url=href,
                    condition=condition,
                    scraped_at=datetime.now(),
                    location=location,
                    description=description or title,
                )
            )

        listings.sort(key=lambda x: x.price)
        logger.info(
            f"Chrono24 IT: {italian_count} card italiani → "
            f"{len(listings)} listing validi per {reference}"
        )

    except Exception as e:
        logger.error(f"Chrono24 IT scrape error per '{reference}': {e}")
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
            locale="it-IT",
            timezone_id="Europe/Rome",
        )
        results = await scrape(reference, context)
        await browser.close()
        return results


if __name__ == "__main__":
    import sys

    ref = sys.argv[1] if len(sys.argv) > 1 else "116610LN"
    found = asyncio.run(scrape_standalone(ref))
    for l in found:
        print(f"{l.price} {l.currency} | {l.condition} | {l.location} | {l.url}")
