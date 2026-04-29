"""
Dealer Scraper — entry point unificato per siti reseller.
Rileva automaticamente CMS (Shopify/WooCommerce/custom) e usa lo scraper appropriato.
"""
import asyncio
import httpx
from urllib.parse import urlparse, unquote
from models.schemas import WatchListing
from utils.logger import get_logger
from scrapers.shopify import scrape_shopify, is_shopify
from scrapers.woocommerce import scrape_woocommerce, is_woocommerce

logger = get_logger("scraper.dealer")

# ── Dealer italiani verificati ─────────────────────────────────────────────────

KNOWN_SHOPIFY_DEALERS = [
    # Italiani verificati
    "ruzzaorologi.com",         # Ruzza Orologi, Milano ✓
    "preziosoparma.it",         # Prezioso Parma ✓
    "ismawatches.it",           # Isma Watch, Broni ✓
    "zorzoliorologi.com",       # Zorzoli Orologi, Pavia ✓
    # Internazionali verificati
    "shop.hodinkee.com",
    "www.analogshift.com",
]

KNOWN_WOO_DEALERS: list[str] = [
    # Italiani verificati
    "edwatch.it",               # Edwatch, Parma ✓
    "eorologi.com",             # eOrologi, Roma ✓
    "www.dellaroccagioielli.com",  # Della Rocca, Bologna ✓
    "www.gioielleriabonanno.it",   # Bonanno, Roma ✓
    "www.msellatiorologi.com",  # Msellati, Roma ✓
    "goldfingersorologi.it",    # Goldfingers, Verona ✓
    "ketervintagewatches.it",   # Keter, Roma ✓
    "cantelliorologi.it",       # Carlo Cantelli, Sassuolo ✓
]

# Cache cms detection {domain: "shopify"|"woocommerce"|"unknown"}
_cms_cache: dict[str, str] = {}


async def detect_and_scrape(domain: str, reference: str) -> list[WatchListing]:
    """
    Rileva il CMS del sito e usa lo scraper appropriato.
    Usa cache per evitare detection ripetuta.
    """
    if domain not in _cms_cache:
        _cms_cache[domain] = await _detect_cms(domain)

    cms = _cms_cache[domain]
    logger.info(f"Dealer {domain}: CMS={cms}")

    if cms == "shopify":
        return await scrape_shopify(domain, reference)
    elif cms == "woocommerce":
        return await scrape_woocommerce(domain, reference)
    else:
        return []  # custom sites: troppo inaffidabili, skip per ora


async def _detect_cms(domain: str) -> str:
    """Rileva CMS tramite endpoint signature (non serve scaricare HTML)."""
    if await is_shopify(domain):
        return "shopify"
    if await is_woocommerce(domain):
        return "woocommerce"
    return "unknown"


async def discover_and_scrape_dealers(reference: str, max_domains: int = 20) -> list[WatchListing]:
    """
    Entry point principale:
    1. Parte dai KNOWN dealers
    2. Cerca nuovi via DuckDuckGo
    3. Rileva CMS e scrapa
    """
    all_listings = []

    # Step 1: scrapa Shopify e WooCommerce in parallelo
    tasks = (
        [scrape_shopify(d, reference) for d in KNOWN_SHOPIFY_DEALERS] +
        [scrape_woocommerce(d, reference) for d in KNOWN_WOO_DEALERS]
    )
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in results:
        if isinstance(r, list):
            all_listings.extend(r)

    logger.info(f"dealer_scraper: {len(all_listings)} totali per {reference}")
    return all_listings


async def _search_watch_dealers(reference: str) -> list[str]:
    """
    Cerca dealer via DuckDuckGo, ritorna lista di domini.
    Esclude marketplace noti (eBay, Chrono24, ecc.).
    """
    EXCLUDE_DOMAINS = {
        "ebay", "chrono24", "amazon", "subito", "catawiki", "watchfinder",
        "instagram", "facebook", "youtube", "twitter", "reddit",
        "wikipedia", "google", "bing",
    }

    queries = [
        f'"{reference}" orologio vendita prezzo €',
        f'"{reference}" watch for sale price',
        f'buy {reference} dealer shop',
    ]

    domains: set[str] = set()

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for query in queries[:2]:  # max 2 query per non fare rate limit
            try:
                r = await client.post(
                    "https://html.duckduckgo.com/html/",
                    data={"q": query, "kl": "it-it"},
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r.text, "html.parser")

                for a in soup.find_all("a", class_="result__url"):
                    href = a.get("href", "")
                    # DDG wrappa in /l/?uddg=
                    if "/l/?uddg=" in href:
                        href = unquote(href.split("uddg=")[-1].split("&")[0])
                    parsed = urlparse(href if href.startswith("http") else f"https://{href}")
                    netloc = parsed.netloc.lower().lstrip("www.")
                    if netloc and not any(ex in netloc for ex in EXCLUDE_DOMAINS):
                        domains.add(parsed.netloc.lower())

                await asyncio.sleep(2)  # rate limit DDG

            except Exception as e:
                logger.debug(f"DDG search error: {e}")

    return list(domains)
