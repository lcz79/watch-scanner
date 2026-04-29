"""
TikTok Discovery Agent.

Trova reseller di orologi su TikTok tramite:
  1. Ricerca per keyword/hashtag
  2. Estrazione account dai video trovati
  3. Scoring basato su descrizione account e contenuto video

Usa Playwright (nessun account richiesto per contenuti pubblici).
"""

import re
import asyncio
from datetime import datetime
from playwright.async_api import BrowserContext
from utils.logger import get_logger
from agents.discovery import resellers_db as db_module
from models.schemas import WatchListing

logger = get_logger("discovery.tiktok")

TIKTOK_SEARCHES = [
    "rolex usato vendita",
    "orologio lusso vendo",
    "watch for sale rolex",
    "submariner vendita",
    "patek philippe usato",
    "audemars piguet vendita",
]

TIKTOK_HASHTAGS = [
    "watchforsale", "rolexforsale", "orologiousato",
    "watchreseller", "luxurywatchforsale", "rolexusato",
]

PRICE_RE = re.compile(r'([\d\.]{3,})\s*[€$]|[€$]\s*([\d\.]{3,})', re.I)


async def run(context: BrowserContext, db: dict) -> int:
    """Entry point principale."""
    new_total = 0

    logger.info("[TikTok] Ricerca per keyword")
    for query in TIKTOK_SEARCHES:
        new = await _search_tiktok(context, db, query)
        new_total += new
        await asyncio.sleep(5)

    logger.info(f"[TikTok] Completato — {new_total} nuovi reseller trovati")
    return new_total


async def _search_tiktok(context: BrowserContext, db: dict, query: str) -> int:
    new = 0
    page = await context.new_page()
    try:
        url = f"https://www.tiktok.com/search/video?q={query.replace(' ', '%20')}"
        logger.info(f"  TikTok search: '{query}'")

        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        # Scrolla per caricare risultati
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(1500)

        # Estrai video e account
        results = await page.evaluate("""
            () => {
                const items = [];
                // Cerca video card
                document.querySelectorAll('a[href*="/@"][href*="/video/"]').forEach(a => {
                    const href = a.href;
                    const match = href.match(/\\/@([^/]+)\\/video\\/(\\d+)/);
                    if (!match) return;
                    const username = match[1];
                    const videoId = match[2];
                    const container = a.closest('[class*="DivItemContainer"], [class*="video-feed-item"]') || a;
                    const text = container.innerText || '';
                    items.push({ username, videoId, text: text.slice(0, 300), url: href });
                });
                return [...new Map(items.map(i => [i.username, i])).values()];
            }
        """)

        logger.info(f"  Trovati {len(results)} account per '{query}'")

        for item in results[:15]:
            username = item.get("username", "")
            if not username or db_module.is_known(db, username):
                continue

            text = item.get("text", "")
            has_price = bool(PRICE_RE.search(text))
            has_sale_kw = any(kw in text.lower() for kw in ["vendo", "vendesi", "for sale", "prezzo", "price", "€"])

            score = 3  # base per essere apparso nella ricerca
            reasons = [f"TikTok search: {query}"]
            if has_price:
                score += 2
                reasons.append("prezzo nel video")
            if has_sale_kw:
                score += 1
                reasons.append("keyword vendita")

            db_module.add_reseller(
                db, username, "tiktok", score, reasons,
                followers=0,
                bio=text[:150],
                discovered_via=f"TikTok search: {query}",
            )
            new += 1
            await asyncio.sleep(1)

    except Exception as e:
        logger.warning(f"  TikTok '{query}' error: {e}")
    finally:
        await page.close()

    return new


async def scrape_listings(context: BrowserContext, reference: str) -> list[WatchListing]:
    """
    Cerca video TikTok con annunci per una referenza specifica.
    Chiamato dal SocialAgent in real mode.
    """
    page = await context.new_page()
    listings = []
    try:
        url = f"https://www.tiktok.com/search/video?q={reference}+orologio+vendita"
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(1200)

        results = await page.evaluate("""
            () => {
                const items = [];
                document.querySelectorAll('a[href*="/@"][href*="/video/"]').forEach(a => {
                    const href = a.href;
                    const match = href.match(/\\/@([^/]+)\\/video\\/(\\d+)/);
                    if (!match) return;
                    const container = a.closest('[class*="DivItemContainer"]') || a;
                    const text = container.innerText || '';
                    items.push({
                        username: match[1],
                        url: href,
                        text: text.slice(0, 300)
                    });
                });
                return [...new Map(items.map(i => [i.url, i])).values()];
            }
        """)

        for item in results[:10]:
            text = item.get("text", "")
            price_match = PRICE_RE.search(text.replace(".", "").replace(",", "."))
            if not price_match:
                continue
            try:
                price = float((price_match.group(1) or price_match.group(2) or "0"))
            except Exception:
                continue
            if price < 500:
                continue

            listings.append(WatchListing(
                source="tiktok",
                reference=reference,
                price=price,
                currency="EUR",
                seller=f"@{item['username']}",
                url=item["url"],
                condition="unknown",
                scraped_at=datetime.now(),
                description=text[:150],
            ))

    except Exception as e:
        logger.warning(f"TikTok scrape error: {e}")
    finally:
        await page.close()

    return listings
