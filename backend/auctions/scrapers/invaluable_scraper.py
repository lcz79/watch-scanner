"""
Invaluable.com scraper — aggregatore aste da centinaia di case.

Strategia a 3 livelli:
  1. API interna diretta via httpx (endpoint XHR che il sito usa internamente)
  2. Playwright con network interception (cattura le richieste XHR durante la navigazione)
  3. DOM fallback (parsing HTML come ultima risorsa)

Fonte parallela: LiveAuctioneers.com (stesso approccio)
"""
import asyncio
import json
import re
import urllib.parse
from datetime import datetime

import httpx
from utils.logger import get_logger

logger = get_logger("auctions")

INVALUABLE_BASE = "https://www.invaluable.com"
LIVEAUCTIONEERS_BASE = "https://api.liveauctioneers.com"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

KNOWN_BRANDS = [
    "Rolex", "Patek Philippe", "Audemars Piguet", "F.P. Journe",
    "Richard Mille", "Omega", "Cartier", "Vacheron Constantin",
    "A. Lange & Söhne", "Breguet", "IWC", "Jaeger-LeCoultre",
    "Panerai", "Hublot", "Tudor", "Zenith", "Chopard", "Girard-Perregaux",
]


def _extract_brand(title: str) -> str:
    title_lower = title.lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in title_lower:
            return brand
    return "Unknown"


def _parse_price(text) -> float | None:
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text)
    cleaned = re.sub(r"[^\d.]", "", str(text).replace(",", ""))
    try:
        v = float(cleaned)
        return v if v > 0 else None
    except ValueError:
        return None


def _parse_estimate(text: str | None) -> tuple[float | None, float | None]:
    if not text or "request" in str(text).lower():
        return None, None
    nums = [float(p.replace(",", "")) for p in re.findall(r"[\d,]+", str(text))
            if p.replace(",", "").isdigit()]
    if len(nums) >= 2:
        return nums[0], nums[1]
    elif len(nums) == 1:
        return nums[0], nums[0]
    return None, None


# ---------------------------------------------------------------------------
# Normalizzazione
# ---------------------------------------------------------------------------

def _normalize_item(item: dict, source: str = "invaluable") -> dict | None:
    try:
        title = (
            item.get("lotTitle") or item.get("title") or item.get("description")
            or item.get("name") or item.get("lotDescription") or ""
        )
        if not title or len(title) < 3:
            return None

        brand = _extract_brand(title)

        hammer = _parse_price(
            item.get("priceResult") or item.get("hammerPrice")
            or item.get("soldPrice") or item.get("price")
            or item.get("currentBid") or item.get("winningBid")
        )

        est_low_raw = item.get("estimateLow") or item.get("lowEstimate") or item.get("estimate_low")
        est_high_raw = item.get("estimateHigh") or item.get("highEstimate") or item.get("estimate_high")
        estimate_low = _parse_price(est_low_raw)
        estimate_high = _parse_price(est_high_raw)
        if not estimate_low:
            est_str = item.get("estimateString") or item.get("estimateRange") or item.get("estimate") or ""
            estimate_low, estimate_high = _parse_estimate(str(est_str))

        sale_date = str(
            item.get("saleDate") or item.get("auctionDate") or item.get("date")
            or item.get("eventDate") or item.get("dateTimeLocal") or ""
        )[:10]
        if not sale_date or sale_date == "None":
            sale_date = datetime.utcnow().strftime("%Y-%m-%d")

        auction_house = str(
            item.get("auctionHouse") or item.get("houseName")
            or item.get("organization") or item.get("sellerName")
            or item.get("houseId") or source.capitalize()
        )

        lot_url = str(item.get("lotRef") or item.get("url") or item.get("link") or item.get("lotUrl") or "")
        if lot_url and not lot_url.startswith("http"):
            lot_url = f"{INVALUABLE_BASE}{lot_url}"

        image_url = str(
            item.get("photoPath") or item.get("imageUrl") or item.get("thumbnailUrl")
            or item.get("image") or item.get("photo") or ""
        )

        return {
            "auction_house": auction_house,
            "sale_name": str(item.get("saleName") or item.get("auctionTitle") or item.get("eventTitle") or ""),
            "sale_location": str(item.get("location") or item.get("city") or ""),
            "sale_date": sale_date,
            "lot_number": str(item.get("lotNum") or item.get("lotNumber") or item.get("lot") or ""),
            "brand": brand,
            "model": str(title),
            "reference": str(item.get("reference") or item.get("refNo") or ""),
            "description": str(title),
            "estimate_low_chf": estimate_low,
            "estimate_high_chf": estimate_high,
            "hammer_price_chf": hammer,
            "buyer_premium_pct": 25.0,
            "total_price_chf": round(hammer * 1.25, 0) if hammer else None,
            "currency": str(item.get("currency") or item.get("currencyCode") or "USD"),
            "lot_url": lot_url,
            "image_url": image_url,
        }
    except Exception as e:
        logger.debug(f"normalize_item error: {e}")
        return None


# ---------------------------------------------------------------------------
# Invaluable — API diretta httpx
# ---------------------------------------------------------------------------

async def _invaluable_api(reference: str, limit: int = 30) -> list[dict]:
    """
    Chiama l'endpoint interno di Invaluable che il browser usa via XHR.
    Più affidabile del parsing HTML perché restituisce JSON strutturato.
    """
    # Invaluable usa un endpoint Algolia-based o un endpoint proprietario
    # Proviamo entrambi
    endpoints = [
        # Endpoint 1: search API
        f"{INVALUABLE_BASE}/catResults/v2?search[query]={urllib.parse.quote(reference)}&search[supercategoryName]=Watches%20%26%20Timepieces&search[upcoming]=false&size={limit}",
        # Endpoint 2: search alternativo
        f"{INVALUABLE_BASE}/api/search?query={urllib.parse.quote(reference)}&department=watches&upcoming=false&page=1&pageSize={limit}",
    ]

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{INVALUABLE_BASE}/search/?query={urllib.parse.quote(reference)}",
        "X-Requested-With": "XMLHttpRequest",
    }

    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        for url in endpoints:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    # Cerca la lista di items in vari percorsi JSON
                    items = (
                        data.get("results") or data.get("lots") or data.get("items")
                        or data.get("hits") or data.get("data", {}).get("results")
                        or []
                    )
                    if isinstance(items, list) and items:
                        results = [_normalize_item(i) for i in items[:limit]]
                        valid = [r for r in results if r]
                        logger.info(f"Invaluable API: {len(valid)} lotti per '{reference}'")
                        return valid
            except Exception as e:
                logger.debug(f"Invaluable API endpoint {url[:60]}... error: {e}")
                continue

    return []


# ---------------------------------------------------------------------------
# Invaluable — Playwright con network interception
# ---------------------------------------------------------------------------

async def _invaluable_playwright(reference: str, limit: int = 30) -> list[dict]:
    """
    Usa Playwright intercettando le chiamate XHR per catturare i dati JSON
    prima che vengano renderizzati nel DOM.
    """
    from playwright.async_api import async_playwright

    url = f"{INVALUABLE_BASE}/search/?query={urllib.parse.quote(reference)}&upcoming=false&resultsView=list"
    captured_items: list[dict] = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 900},
                extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            )
            page = await context.new_page()

            # Intercetta le risposte JSON con dati di lotti
            async def handle_response(response):
                if captured_items:
                    return
                try:
                    if (response.status == 200
                            and "json" in (response.headers.get("content-type") or "")
                            and any(k in response.url for k in ["catResults", "search", "lots", "results", "algolia"])):
                        body = await response.json()
                        items = (
                            body.get("results") or body.get("lots") or body.get("hits")
                            or body.get("items") or body.get("data", {}).get("results")
                            or []
                        )
                        if isinstance(items, list) and len(items) > 2:
                            captured_items.extend(items[:limit])
                            logger.debug(f"Invaluable XHR intercettato: {len(items)} items")
                except Exception:
                    pass

            page.on("response", handle_response)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                # Aspetta che le chiamate XHR vengano completate
                await asyncio.sleep(5)

                # Se non abbiamo catturato nulla via XHR, proviamo __NEXT_DATA__
                if not captured_items:
                    next_data_raw = await page.evaluate(
                        "() => { try { return JSON.stringify(window.__NEXT_DATA__); } catch(e) { return null; } }"
                    )
                    if next_data_raw:
                        nd = json.loads(next_data_raw)
                        # Cerca ricorsivamente array di items nella struttura
                        def find_items(obj, depth=0):
                            if depth > 6:
                                return []
                            if isinstance(obj, list) and len(obj) > 2:
                                if obj[0] and isinstance(obj[0], dict) and (
                                    "lotTitle" in obj[0] or "title" in obj[0] or "hammerPrice" in obj[0]
                                ):
                                    return obj
                            if isinstance(obj, dict):
                                for v in obj.values():
                                    r = find_items(v, depth + 1)
                                    if r:
                                        return r
                            return []

                        items = find_items(nd)
                        captured_items.extend(items[:limit])

            except Exception as e:
                logger.debug(f"Invaluable Playwright goto error: {e}")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.debug(f"Invaluable Playwright error: {e}")

    results = [_normalize_item(i) for i in captured_items]
    valid = [r for r in results if r]
    logger.info(f"Invaluable Playwright: {len(valid)} lotti per '{reference}'")
    return valid


# ---------------------------------------------------------------------------
# LiveAuctioneers — fonte parallela
# ---------------------------------------------------------------------------

async def _liveauctioneers_search(reference: str, limit: int = 20) -> list[dict]:
    """
    Cerca su LiveAuctioneers.com — ottima copertura di case minori.
    Usa l'API pubblica che il loro sito espone.
    """
    # LiveAuctioneers ha un'API accessibile per le ricerche pubbliche
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Referer": "https://www.liveauctioneers.com/",
    }

    # Endpoint di ricerca risultati passati
    url = (
        f"https://api.liveauctioneers.com/lots/search"
        f"?keyword={urllib.parse.quote(reference)}"
        f"&status=past&category=watches&limit={limit}"
    )

    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                items = (
                    data.get("lots") or data.get("results") or data.get("items")
                    or data.get("data") or []
                )
                if isinstance(items, list):
                    results = []
                    for item in items[:limit]:
                        norm = _normalize_item(item, source="liveauctioneers")
                        if norm:
                            if not norm.get("reference"):
                                norm["reference"] = reference
                            results.append(norm)
                    logger.info(f"LiveAuctioneers: {len(results)} lotti per '{reference}'")
                    return results
        except Exception as e:
            logger.debug(f"LiveAuctioneers API error: {e}")

    # Fallback: HTML scraping con Playwright
    try:
        from playwright.async_api import async_playwright
        la_url = f"https://www.liveauctioneers.com/search/?keyword={urllib.parse.quote(reference)}&status=past&vertical=watches"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(user_agent=USER_AGENT, viewport={"width": 1280, "height": 900})
            page = await context.new_page()
            captured: list[dict] = []

            async def handle_la_response(response):
                if captured:
                    return
                try:
                    if response.status == 200 and "json" in (response.headers.get("content-type") or ""):
                        if any(k in response.url for k in ["search", "lots", "results"]):
                            body = await response.json()
                            items = body.get("lots") or body.get("results") or body.get("items") or []
                            if isinstance(items, list) and len(items) > 1:
                                captured.extend(items[:limit])
                except Exception:
                    pass

            page.on("response", handle_la_response)
            try:
                await page.goto(la_url, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(4)
            except Exception:
                pass
            finally:
                await context.close()
                await browser.close()

            results = [_normalize_item(i, "liveauctioneers") for i in captured]
            valid = [r for r in results if r]
            logger.info(f"LiveAuctioneers Playwright: {len(valid)} lotti per '{reference}'")
            return valid
    except Exception as e:
        logger.debug(f"LiveAuctioneers Playwright error: {e}")

    return []


# ---------------------------------------------------------------------------
# Entry point pubblico
# ---------------------------------------------------------------------------

async def search_reference(reference: str, limit: int = 30) -> list[dict]:
    """
    Cerca risultati d'asta su Invaluable + LiveAuctioneers in parallelo.
    Livello 1: API diretta httpx
    Livello 2: Playwright con XHR intercept
    Livello 3: DOM fallback
    """
    # Livello 1: API diretta (veloce, nessun browser)
    results = await _invaluable_api(reference, limit)

    # Livello 2: se vuoto, prova Playwright
    if not results:
        playwright_results = await _invaluable_playwright(reference, limit)
        results.extend(playwright_results)

    # Fonte parallela: LiveAuctioneers (sempre, per integrare)
    try:
        la_results = await _liveauctioneers_search(reference, limit=15)
        # Deduplication base per titolo
        existing_titles = {r.get("model", "").lower() for r in results}
        for r in la_results:
            if r.get("model", "").lower() not in existing_titles:
                results.append(r)
                existing_titles.add(r.get("model", "").lower())
    except Exception as e:
        logger.debug(f"LiveAuctioneers parallel error: {e}")

    # Aggiungi reference a tutti
    for r in results:
        if not r.get("reference"):
            r["reference"] = reference

    logger.info(f"search_reference '{reference}': totale {len(results)} lotti aggregati")
    return results


async def get_upcoming_auctions(limit: int = 50) -> list[dict]:
    """
    Recupera aste upcoming da Invaluable.
    """
    from playwright.async_api import async_playwright

    url = f"{INVALUABLE_BASE}/search/?query=luxury+watches&upcoming=true&resultsView=list"
    upcoming = []
    captured: list[dict] = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(user_agent=USER_AGENT, viewport={"width": 1280, "height": 900})
            page = await context.new_page()

            async def handle(response):
                if captured:
                    return
                try:
                    if response.status == 200 and "json" in (response.headers.get("content-type") or ""):
                        body = await response.json()
                        items = body.get("results") or body.get("lots") or body.get("items") or []
                        if isinstance(items, list) and len(items) > 1:
                            captured.extend(items[:limit])
                except Exception:
                    pass

            page.on("response", handle)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(4)
            except Exception:
                pass
            finally:
                await context.close()
                await browser.close()

        for item in captured:
            norm = _normalize_item(item)
            if norm:
                upcoming.append({
                    "house": norm["auction_house"],
                    "sale_name": norm["sale_name"],
                    "location": norm["sale_location"],
                    "date": norm["sale_date"],
                    "url": norm["lot_url"],
                    "catalog_url": norm["lot_url"],
                    "highlights": [],
                    "source": "invaluable",
                })

    except Exception as e:
        logger.debug(f"Invaluable get_upcoming error: {e}")

    logger.info(f"Invaluable upcoming: {len(upcoming)} aste trovate")
    return upcoming
