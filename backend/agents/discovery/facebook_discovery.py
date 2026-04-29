"""
Facebook Discovery Agent.

Trova reseller di orologi su Facebook tramite:
  1. Facebook Marketplace — annunci pubblici di orologi in vendita
  2. Facebook Groups — gruppi di compravendita orologi (pubblici)

Usa Playwright (nessun account richiesto per Marketplace pubblico).
Per i gruppi privati serve un account Facebook (opzionale).
"""

import re
import asyncio
from datetime import datetime
from playwright.async_api import BrowserContext
from utils.logger import get_logger
from agents.discovery import resellers_db as db_module
from models.schemas import WatchListing

logger = get_logger("discovery.facebook")

# Gruppi Facebook pubblici di compravendita orologi
FB_GROUPS = [
    "compraveditaorologi",
    "orologi-usati-italia",
    "watchforsaleitaly",
    "rolex-usato-italia",
    "orologi-di-lusso-usati",
    "watch-trading-europe",
]

MARKETPLACE_SEARCHES = [
    "rolex usato",
    "orologio lusso vendita",
    "submariner vendita",
    "patek philippe usato",
    "audemars piguet usato",
    "omega seamaster usato",
]

PRICE_RE = re.compile(r'([\d\.]+)[,\.]?(\d{2})?\s*[€$]|[€$]\s*([\d\.]+)', re.I)


async def run(context: BrowserContext, db: dict) -> int:
    """Entry point principale."""
    new_total = 0

    logger.info("[Facebook] Fase 1: Facebook Marketplace")
    for search in MARKETPLACE_SEARCHES:
        new = await _scrape_marketplace(context, db, search)
        new_total += new
        await asyncio.sleep(4)

    logger.info(f"[Facebook] Completato — {new_total} nuovi reseller trovati")
    return new_total


async def _scrape_marketplace(context: BrowserContext, db: dict, search_query: str) -> int:
    """
    Scrapa Facebook Marketplace per una query di ricerca.
    Raccoglie i venditori e i loro listing.
    """
    new = 0
    page = await context.new_page()
    try:
        # Marketplace pubblico IT, categoria orologi, 500km da Milano
        url = (
            f"https://www.facebook.com/marketplace/category/watches"
            f"?query={search_query.replace(' ', '%20')}"
            f"&exact=false"
        )
        logger.info(f"  FB Marketplace: '{search_query}'")
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        # Scrolla per caricare più annunci
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 1000)")
            await page.wait_for_timeout(1500)

        # Estrai listing individuali
        listings_data = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('[data-testid="marketplace_feed_item"], [class*="x1i10hfl"][href*="/marketplace/item/"]');
                const results = [];
                document.querySelectorAll('a[href*="/marketplace/item/"]').forEach(a => {
                    const text = a.innerText || '';
                    const priceMatch = text.match(/([\\d\\.]+)[,\\.]?(\\d{2})?\\s*[€$]/);
                    if (priceMatch) {
                        results.push({
                            url: 'https://www.facebook.com' + a.getAttribute('href').split('?')[0],
                            text: text.trim().slice(0, 300),
                            price_raw: priceMatch[0]
                        });
                    }
                });
                return [...new Map(results.map(r => [r.url, r])).values()];
            }
        """)

        logger.info(f"  Trovati {len(listings_data)} annunci per '{search_query}'")

        for item in listings_data[:20]:
            # Estrai seller dalla pagina dell'annuncio se necessario
            seller_name = f"fb_marketplace_{search_query.replace(' ', '_')}"
            price = _parse_price(item.get("price_raw", ""))
            if not price or price < 500:
                continue

            # Salva come reseller Facebook con score base
            username = f"fb_{item['url'].split('/item/')[-1].rstrip('/')}"
            if not db_module.is_known(db, username):
                db_module.add_reseller(
                    db, username, "facebook",
                    score=3,
                    reasons=["FB Marketplace listing", f"prezzo: {price}€"],
                    followers=0,
                    bio=item.get("text", "")[:200],
                    discovered_via=f"FB Marketplace: {search_query}",
                )
                new += 1

        await asyncio.sleep(2)

    except Exception as e:
        logger.warning(f"  FB Marketplace '{search_query}' error: {e}")
    finally:
        await page.close()

    return new


def _parse_price(text: str) -> float | None:
    m = PRICE_RE.search(text.replace(".", "").replace(",", "."))
    if m:
        try:
            return float(m.group(1))
        except Exception:
            pass
    return None


async def scrape_listings(context: BrowserContext, reference: str) -> list[WatchListing]:
    """
    Cerca annunci specifici per una referenza su Facebook Marketplace.
    Chiamato dal MarketplaceAgent in real mode.
    """
    page = await context.new_page()
    listings = []
    try:
        url = f"https://www.facebook.com/marketplace/category/watches?query={reference}"
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(1200)

        items = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('a[href*="/marketplace/item/"]').forEach(a => {
                    const text = a.innerText || '';
                    const priceMatch = text.match(/([\\d\\.]+)[,\\.]?(\\d{2})?\\s*[€$]/);
                    const imgEl = a.querySelector('img');
                    if (priceMatch) {
                        results.push({
                            url: 'https://www.facebook.com' + a.getAttribute('href').split('?')[0],
                            text: text.trim().slice(0, 200),
                            price_raw: priceMatch[0],
                            image: imgEl ? imgEl.src : null
                        });
                    }
                });
                return [...new Map(results.map(r => [r.url, r])).values()];
            }
        """)

        for item in items[:15]:
            price = _parse_price(item.get("price_raw", ""))
            if not price or price < 1000:
                continue
            listings.append(WatchListing(
                source="facebook",
                reference=reference,
                price=price,
                currency="EUR",
                seller="Facebook Marketplace",
                url=item["url"],
                condition="unknown",
                scraped_at=datetime.now(),
                description=item.get("text", "")[:150],
                image_url=item.get("image"),
            ))

    except Exception as e:
        logger.warning(f"FB Marketplace scrape error: {e}")
    finally:
        await page.close()

    return listings
