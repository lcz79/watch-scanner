"""
Facebook Marketplace Scraper per WatchScanner.

Strategia:
  1. Playwright → marketplace.facebook.com/search?query=<referenza+orologio>
  2. Filtra solo annunci orologi (no accessori/ricambi)
  3. Gestisce cookies Facebook opzionali per aggirare il rate-limiting
  4. Pagination: max 2 pagine per run

Requisiti:
  FACEBOOK_COOKIES (opzionale, .env) — JSON dei cookie sessione Facebook.
  Se assente, usa Marketplace in modalità pubblica (più limitata).

Uso:
  from scrapers.facebook_marketplace import scrape
  listings = await scrape("116610LN")
  # oppure con contesto Playwright esistente:
  listings = await scrape_with_context("116610LN", browser_context)
"""

import asyncio
import json
import re
from datetime import datetime
from utils.logger import get_logger
from models.schemas import WatchListing

logger = get_logger("scraper.facebook_marketplace")

# ── Costanti ─────────────────────────────────────────────────────────────────

SCRAPE_TIMEOUT = 30_000  # ms per Playwright
MAX_SCROLL_ROUNDS = 3
MAX_ITEMS_PER_PAGE = 20

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Parole che indicano che il listing è un orologio (non un accessorio o pezzo di ricambio)
WATCH_SIGNALS = [
    "orologio", "orologi", "watch", "timepiece",
    "submariner", "daytona", "datejust", "gmt", "seamaster", "speedmaster",
    "nautilus", "royal oak", "black bay",
    "acciaio", "steel", "oro", "gold", "automatico", "automatic",
    "rolex", "omega", "patek", "audemars", "tudor", "breitling", "iwc",
    "panerai", "hublot", "vacheron", "cartier",
]

# Parole che indicano NON un orologio (accessori, cinturini, ricambi, scatole vuote)
NON_WATCH_SIGNALS = [
    "cinturino solo", "only strap", "solo cinturino", "bracelet only",
    "vetro rotto", "ricambio", "spare part", "scatola vuota", "empty box",
    "corona di ricambio",
]

# ── Regex prezzo ──────────────────────────────────────────────────────────────

from scrapers.stories.ocr import (
    _parse_price,
    _detect_reference,
    _detect_brand,
    _detect_condition,
    _is_watch_related,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_watch_listing(text: str) -> bool:
    """
    Controlla che il listing sia effettivamente un orologio e non un accessorio.
    """
    text_lower = text.lower()
    # Deve avere segnali positivi
    if not any(sig in text_lower for sig in WATCH_SIGNALS):
        return False
    # Non deve avere segnali negativi
    if any(sig in text_lower for sig in NON_WATCH_SIGNALS):
        return False
    return True


def _build_search_url(reference: str, page_cursor: str = "") -> str:
    """
    Costruisce l'URL di ricerca per Facebook Marketplace.
    Usa la categoria watches per filtrare automaticamente.
    """
    query = f"{reference} orologio"
    base = (
        f"https://www.facebook.com/marketplace/search"
        f"?query={query.replace(' ', '%20')}"
        f"&category_id=watches"
        f"&exact=false"
    )
    if page_cursor:
        base += f"&cursor={page_cursor}"
    return base


def _load_facebook_cookies() -> list[dict] | None:
    """
    Carica i cookie Facebook dalla configurazione (.env FACEBOOK_COOKIES).
    Formato atteso: JSON array di oggetti cookie Playwright.
    """
    try:
        from config import get_settings
        settings = get_settings()
        raw = getattr(settings, "facebook_cookies", None)
        if not raw:
            return None
        cookies = json.loads(raw)
        if isinstance(cookies, list):
            logger.debug(f"Facebook cookies caricati: {len(cookies)} cookie")
            return cookies
    except Exception as e:
        logger.debug(f"Facebook cookies parse error: {e}")
    return None


async def _extract_listings_from_page(page, reference: str) -> list[dict]:
    """
    Estrae dati grezzi di tutti gli annunci nella pagina corrente.
    Usa JavaScript per attraversare il DOM di Marketplace.
    """
    try:
        items = await page.evaluate("""
            () => {
                const results = [];
                // Selettori Marketplace (Facebook cambia spesso le classi)
                const selectors = [
                    'a[href*="/marketplace/item/"]',
                    '[data-testid="marketplace_feed_item"] a',
                ];
                const seen = new Set();

                for (const sel of selectors) {
                    document.querySelectorAll(sel).forEach(a => {
                        // Normalizza URL (rimuovi query string con trackers)
                        const rawHref = a.getAttribute('href') || '';
                        const itemMatch = rawHref.match(/\\/marketplace\\/item\\/(\\d+)/);
                        if (!itemMatch) return;

                        const itemId = itemMatch[1];
                        if (seen.has(itemId)) return;
                        seen.add(itemId);

                        const url = 'https://www.facebook.com/marketplace/item/' + itemId + '/';

                        // Raccoglie tutto il testo visibile nell'elemento o nei suoi antenati
                        let container = a;
                        for (let i = 0; i < 4; i++) {
                            const parent = container.parentElement;
                            if (!parent) break;
                            container = parent;
                            if (container.innerText && container.innerText.length > 30) break;
                        }
                        const text = (container.innerText || a.innerText || '').trim().slice(0, 400);

                        // Cerca prezzo nel testo dell'elemento
                        const priceMatch = text.match(
                            /([\\d]{1,3}(?:[.,][\\d]{3})+(?:[.,]\\d{1,2})?|[\\d]{3,6}(?:[.,]\\d{1,2})?)\\s*[€£$]|[€£$]\\s*([\\d]{1,3}(?:[.,][\\d]{3})+)/
                        );

                        // Immagine
                        const img = container.querySelector('img[src*="fbcdn"]') ||
                                    container.querySelector('img');

                        results.push({
                            url,
                            item_id: itemId,
                            text,
                            price_raw: priceMatch ? priceMatch[0] : '',
                            image: img ? img.src : null,
                        });
                    });
                }
                return results;
            }
        """)
        return items or []
    except Exception as e:
        logger.debug(f"Facebook extract JS error: {e}")
        return []


async def _scrape_single_page(
    page,
    reference: str,
    results: list[WatchListing],
    seen_urls: set[str],
) -> bool:
    """
    Scrapa una singola pagina di risultati Marketplace.
    Ritorna True se ci sono probabilmente più pagine (ha trovato molti risultati).
    """
    # Scrolla per caricare il feed lazy
    for _ in range(MAX_SCROLL_ROUNDS):
        await page.evaluate("window.scrollBy(0, 900)")
        await asyncio.sleep(1.5)

    items = await _extract_listings_from_page(page, reference)
    logger.debug(f"Facebook Marketplace: {len(items)} annunci raw trovati")

    ref_clean = reference.replace(" ", "").upper()

    for item in items[:MAX_ITEMS_PER_PAGE]:
        item_url = item.get("url", "")
        if not item_url or item_url in seen_urls:
            continue

        text = item.get("text", "")
        price_raw = item.get("price_raw", "")

        # Controlla che sia un orologio
        if not _is_watch_listing(text):
            continue

        # Controlla presenza referenza nel testo (loose match)
        text_upper = text.upper()
        ref_match = ref_clean in text_upper or reference.upper() in text_upper
        brand_found = _detect_brand(text)
        if not ref_match and not brand_found:
            # Accetta solo se c'è almeno il brand del watch
            continue

        # Estrai prezzo
        price = _parse_price(price_raw) or _parse_price(text)
        if not price or price < 1000:
            continue

        # Estrai referenza e condizione
        detected_ref = _detect_reference(text) or reference
        condition = _detect_condition(text)

        listing = WatchListing(
            source="facebook_marketplace",
            reference=detected_ref,
            price=price,
            currency="EUR",
            seller="Facebook Marketplace",
            url=item_url,
            condition=condition,
            scraped_at=datetime.now(),
            image_url=item.get("image"),
            description=text[:200],
        )
        seen_urls.add(item_url)
        results.append(listing)

    # Se ha trovato il massimo di item, probabilmente ci sono altre pagine
    return len(items) >= MAX_ITEMS_PER_PAGE


# ── Funzione con contesto Playwright esistente ────────────────────────────────

async def scrape_with_context(reference: str, context) -> list[WatchListing]:
    """
    Scrapa Facebook Marketplace usando un contesto Playwright già aperto.
    Utile quando il SocialAgent gestisce un browser condiviso.

    Args:
        reference: referenza orologio
        context:   BrowserContext Playwright

    Returns:
        Lista di WatchListing con source="facebook_marketplace"
    """
    results: list[WatchListing] = []
    seen_urls: set[str] = set()

    page = await context.new_page()
    try:
        url = _build_search_url(reference)
        logger.info(f"Facebook Marketplace: cercando '{reference}' → {url}")

        await page.goto(url, timeout=SCRAPE_TIMEOUT, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        # Chiudi eventuali overlay login
        for text in ["Non ora", "Not Now", "Chiudi", "Close", "Rifiuta"]:
            try:
                await page.click(f'text="{text}"', timeout=2000)
                await asyncio.sleep(0.5)
            except Exception:
                pass

        # Pagina 1
        has_more = await _scrape_single_page(page, reference, results, seen_urls)

        # Pagina 2 (se disponibile) — scroll bottom-of-page per trigger lazy load
        if has_more and len(results) < MAX_ITEMS_PER_PAGE:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
            await _scrape_single_page(page, reference, results, seen_urls)

    except Exception as e:
        logger.warning(f"Facebook Marketplace scrape error: {e}")
    finally:
        await page.close()

    logger.info(f"Facebook Marketplace: {len(results)} listing per {reference}")
    return results


# ── Entry point pubblico (standalone, gestisce browser) ──────────────────────

async def scrape(reference: str) -> list[WatchListing]:
    """
    Cerca annunci su Facebook Marketplace per la referenza specificata.
    Gestisce autonomamente il browser Playwright e i cookie Facebook.

    Args:
        reference: referenza orologio es. "116610LN", "5711/1A"

    Returns:
        Lista di WatchListing con source="facebook_marketplace"
    """
    from playwright.async_api import async_playwright

    results: list[WatchListing] = []
    seen_urls: set[str] = set()

    # Carica cookie Facebook opzionali
    fb_cookies = _load_facebook_cookies()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=_UA,
            locale="it-IT",
            timezone_id="Europe/Rome",
            viewport={"width": 1280, "height": 900},
        )

        # Applica cookie se disponibili
        if fb_cookies:
            try:
                await context.add_cookies(fb_cookies)
                logger.debug(f"Facebook: {len(fb_cookies)} cookie applicati")
            except Exception as e:
                logger.debug(f"Facebook cookies add error: {e}")

        page = await context.new_page()
        try:
            url = _build_search_url(reference)
            logger.info(f"Facebook Marketplace: cercando '{reference}'")
            await page.goto(url, timeout=SCRAPE_TIMEOUT, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # Gestisci overlay login/cookie-consent di Facebook
            for btn_text in [
                "Rifiuta cookie facoltativi",
                "Decline optional cookies",
                "Non ora",
                "Not Now",
                "Chiudi",
                "Close",
                "Continua senza accedere",
            ]:
                try:
                    await page.click(f'text="{btn_text}"', timeout=2000)
                    await asyncio.sleep(1)
                except Exception:
                    pass

            # Prova anche con selettori aria per i dialog
            for aria_label in ["Chiudi", "Close", "Rifiuta"]:
                try:
                    await page.click(f'[aria-label="{aria_label}"]', timeout=1500)
                    await asyncio.sleep(0.5)
                except Exception:
                    pass

            # Pagina 1
            has_more = await _scrape_single_page(page, reference, results, seen_urls)

            # Pagina 2 — scroll fino in fondo per caricare altri risultati
            if has_more:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)
                await _scrape_single_page(page, reference, results, seen_urls)

            # Query alternativa: brand + "usato" (cattura listing senza referenza)
            if len(results) < 3:
                brand = _detect_brand(reference) or ""
                if brand:
                    alt_url = (
                        f"https://www.facebook.com/marketplace/search"
                        f"?query={brand}%20usato%20orologio"
                        f"&category_id=watches"
                    )
                    await page.goto(alt_url, timeout=SCRAPE_TIMEOUT, wait_until="domcontentloaded")
                    await asyncio.sleep(3)
                    await _scrape_single_page(page, reference, results, seen_urls)

        except Exception as e:
            logger.warning(f"Facebook Marketplace error: {e}")
        finally:
            await page.close()
            await context.close()
            await browser.close()

    # Deduplicazione finale
    seen: set[str] = set()
    unique = [l for l in results if not (l.url in seen or seen.add(l.url))]  # type: ignore[func-returns-value]

    logger.info(f"Facebook Marketplace: {len(unique)} listing unici per {reference}")
    return unique
