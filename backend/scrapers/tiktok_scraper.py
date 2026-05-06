"""
TikTok Scraper per WatchScanner.

Strategia:
  1. TikTok oEmbed API (pubblica, no auth) per singolo video
  2. TikTok webapp "search" endpoint (non ufficiale, no auth per ricerca pubblica)
  3. Playwright come fallback per rendering JS

Hashtag cercati:
  #watchforsale #rolexforsale #orologi #orologi_lusso #watchdealer
  #orologiousato #watchreseller #luxurywatchforsale

Requisiti:
  TIKTOK_SESSION_ID (opzionale, .env) — cookie sessionid per risultati autenticati.
  Se assente, usa solo endpoint pubblici.

Uso:
  from scrapers.tiktok_scraper import scrape
  listings = await scrape("116610LN")
"""

import asyncio
from datetime import datetime
from utils.logger import get_logger
from models.schemas import WatchListing

logger = get_logger("scraper.tiktok")

# ── Costanti ─────────────────────────────────────────────────────────────────

SCRAPE_TIMEOUT = 30.0  # secondi

HASHTAGS = [
    "watchforsale",
    "rolexforsale",
    "orologi",
    "orologiousato",
    "watchdealer",
    "watchreseller",
    "luxurywatchforsale",
    "orologi_lusso",
    "rolexusato",
    "patekphilippeforsale",
]

# Hashtag specifici per brand (derivati dalla referenza)
_BRAND_HASHTAGS: dict[str, list[str]] = {
    "rolex": ["rolexforsale", "rolexusato", "rolexsubmariner"],
    "patek": ["patekphilippeforsale", "patekphilippe", "patekusato"],
    "ap": ["audemarspiguet", "royaloakforsale", "apwatch"],
    "omega": ["omegaforsale", "omegawatch", "speedmaster"],
    "tudor": ["tudorwatch", "blackbay", "tudorforsale"],
}

# Headers comuni per sembrare un browser reale
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.tiktok.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

# ── Regex prezzo (usa le stesse regole OCR per consistenza) ──────────────────

from scrapers.stories.ocr import (
    _parse_price,
    _detect_reference,
    _detect_brand,
    _detect_condition,
    _detect_availability,
    _is_watch_related,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _hashtags_for_reference(reference: str) -> list[str]:
    """Genera lista di hashtag da cercare partendo dalla referenza."""
    ref_clean = reference.replace("/", "").replace(" ", "").lower()
    tags = [ref_clean]

    ref_upper = reference.upper()
    if any(ref_upper.startswith(p) for p in ("116", "126", "228", "124", "114")):
        tags.extend(_BRAND_HASHTAGS["rolex"])
    elif ref_upper.startswith(("57", "51", "53", "59")):
        tags.extend(_BRAND_HASHTAGS["patek"])
    elif ref_upper.startswith(("15", "26", "77")):
        tags.extend(_BRAND_HASHTAGS["ap"])
    elif ref_upper.startswith(("321", "232", "220")):
        tags.extend(_BRAND_HASHTAGS["omega"])
    elif ref_upper.startswith(("M79", "79")):
        tags.extend(_BRAND_HASHTAGS["tudor"])

    tags.extend(HASHTAGS)
    # Deduplicazione preservando ordine
    seen: set[str] = set()
    return [t for t in tags if not (t in seen or seen.add(t))]  # type: ignore[func-returns-value]


def _video_to_listing(
    reference: str,
    video_url: str,
    username: str,
    caption: str,
    thumbnail_url: str | None = None,
    created_at: datetime | None = None,
) -> WatchListing | None:
    """
    Tenta di creare un WatchListing da un video TikTok.
    Ritorna None se il video non contiene un listing valido (no prezzo / non orologio).
    """
    if not _is_watch_related(caption):
        return None

    price = _parse_price(caption)
    if not price:
        return None

    ref_clean = reference.replace(" ", "").upper()
    caption_upper = caption.upper()
    if ref_clean and ref_clean not in caption_upper and reference.upper() not in caption_upper:
        # Anche se non menziona esplicitamente la referenza, teniamo
        # solo se menziona termini di vendita + brand
        if not _detect_brand(caption):
            return None

    detected_ref = _detect_reference(caption) or reference
    condition = _detect_condition(caption)

    return WatchListing(
        source="tiktok",
        reference=detected_ref,
        price=price,
        currency="EUR",
        seller=f"@{username}",
        url=video_url,
        condition=condition,
        scraped_at=created_at or datetime.now(),
        image_url=thumbnail_url,
        description=caption[:200],
    )


# ── Scraping via httpx (endpoint pubblici non ufficiali) ─────────────────────

async def _search_via_webapp(
    client,
    query: str,
    reference: str,
    results: list[WatchListing],
    seen_urls: set[str],
) -> None:
    """
    Chiama il search endpoint non ufficiale di TikTok (webapp).
    Aggiunge listing trovati a `results` (in-place).
    """
    # TikTok exposes a public search endpoint (no auth required for basic results)
    search_url = "https://www.tiktok.com/api/search/general/full/"
    params = {
        "keyword": query,
        "offset": 0,
        "count": 20,
        "search_id": "",
    }
    try:
        resp = await client.get(search_url, params=params, timeout=SCRAPE_TIMEOUT)
        if resp.status_code != 200:
            logger.debug(f"TikTok search HTTP {resp.status_code} per '{query}'")
            return
        data = resp.json()
    except Exception as e:
        logger.debug(f"TikTok search error '{query}': {e}")
        return

    items = data.get("data", [])
    logger.debug(f"TikTok search '{query}': {len(items)} risultati raw")

    for item in items:
        # La risposta può contenere video o account; ci interessano i video
        item_type = item.get("item_type", 0)
        video_info = item.get("item", {})
        if not video_info and item_type != 1:
            continue

        try:
            author = video_info.get("author", {})
            username = author.get("uniqueId") or author.get("unique_id", "unknown")
            video_id = video_info.get("id", "")
            caption = video_info.get("desc", "")
            video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"

            if video_url in seen_urls:
                continue

            thumb_url = None
            video_cover = video_info.get("video", {}).get("cover")
            if video_cover:
                thumb_url = video_cover

            ts_raw = video_info.get("createTime")
            created_at = datetime.fromtimestamp(int(ts_raw)) if ts_raw else None

            listing = _video_to_listing(reference, video_url, username, caption, thumb_url, created_at)
            if listing:
                seen_urls.add(video_url)
                results.append(listing)
        except Exception as e:
            logger.debug(f"TikTok item parse error: {e}")


async def _search_via_oembed(
    client,
    video_url: str,
    reference: str,
    results: list[WatchListing],
    seen_urls: set[str],
) -> None:
    """
    Usa l'oEmbed API pubblica di TikTok per arricchire un video URL già noto.
    https://www.tiktok.com/oembed?url=<video_url>
    """
    if video_url in seen_urls:
        return
    try:
        resp = await client.get(
            "https://www.tiktok.com/oembed",
            params={"url": video_url},
            timeout=10.0,
        )
        if resp.status_code != 200:
            return
        data = resp.json()
    except Exception as e:
        logger.debug(f"oEmbed error {video_url}: {e}")
        return

    caption = data.get("title", "")
    username = data.get("author_name", "unknown")
    thumb_url = data.get("thumbnail_url")

    listing = _video_to_listing(reference, video_url, username, caption, thumb_url)
    if listing:
        seen_urls.add(video_url)
        results.append(listing)


# ── Scraping via Playwright (fallback) ────────────────────────────────────────

async def _search_via_playwright(
    reference: str,
    hashtag: str,
    results: list[WatchListing],
    seen_urls: set[str],
    session_id: str | None = None,
) -> None:
    """
    Fallback Playwright per cercare video TikTok su hashtag / query.
    Gestisce il rendering JS della pagina di ricerca.
    """
    from playwright.async_api import async_playwright

    _UA = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # Query: "referenza + hashtag + vendita"
    query = f"{reference} {hashtag} vendita"
    search_url = f"https://www.tiktok.com/search/video?q={query.replace(' ', '%20')}"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        cookies = []
        if session_id:
            cookies = [
                {
                    "name": "sessionid",
                    "value": session_id,
                    "domain": ".tiktok.com",
                    "path": "/",
                }
            ]

        context = await browser.new_context(
            user_agent=_UA,
            locale="it-IT",
            viewport={"width": 1280, "height": 900},
        )
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()
        try:
            await page.goto(search_url, timeout=int(SCRAPE_TIMEOUT * 1000), wait_until="domcontentloaded")
            await asyncio.sleep(4)

            # Scrolla per caricare più video
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(1.5)

            # Estrai video dalla pagina
            items = await page.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll('a[href*="/@"][href*="/video/"]').forEach(a => {
                        const href = a.href;
                        const match = href.match(/\\/@([^/]+)\\/video\\/(\\d+)/);
                        if (!match) return;
                        const container = a.closest(
                            '[data-e2e="search_video-item"], [class*="DivItemContainer"]'
                        ) || a.parentElement || a;
                        const text = (container.innerText || '').slice(0, 400);
                        const img = container.querySelector('img');
                        results.push({
                            username: match[1],
                            video_id: match[2],
                            url: href.split('?')[0],
                            caption: text,
                            thumbnail: img ? img.src : null,
                        });
                    });
                    return [...new Map(results.map(i => [i.url, i])).values()];
                }
            """)

            logger.debug(f"TikTok Playwright '{hashtag}': {len(items)} video trovati")

            for item in items[:15]:
                video_url = item.get("url", "")
                if not video_url or video_url in seen_urls:
                    continue

                caption = item.get("caption", "")
                username = item.get("username", "unknown")
                thumb = item.get("thumbnail")

                listing = _video_to_listing(reference, video_url, username, caption, thumb)
                if listing:
                    seen_urls.add(video_url)
                    results.append(listing)

        except Exception as e:
            logger.debug(f"TikTok Playwright error '{hashtag}': {e}")
        finally:
            await context.close()
            await browser.close()


# ── Entry point pubblico ──────────────────────────────────────────────────────

async def scrape(reference: str) -> list[WatchListing]:
    """
    Cerca video TikTok di reseller che vendono la referenza specificata.

    Strategia a cascata:
      1. httpx → TikTok search webapp API (non ufficiale, veloce)
      2. Playwright fallback per gli hashtag più rilevanti

    Args:
        reference: referenza orologio es. "116610LN", "5711/1A"

    Returns:
        Lista di WatchListing con source="tiktok"
    """
    results: list[WatchListing] = []
    seen_urls: set[str] = set()

    # Ottieni session_id da config se disponibile
    session_id: str | None = None
    try:
        from config import get_settings
        settings = get_settings()
        session_id = getattr(settings, "tiktok_session_id", None) or None
    except Exception:
        pass

    hashtags = _hashtags_for_reference(reference)[:5]  # max 5 hashtag per run
    queries = [f"{reference} {h}" for h in hashtags[:3]]

    # Costruisci cookies httpx se session disponibile
    httpx_cookies: dict[str, str] = {}
    if session_id:
        httpx_cookies["sessionid"] = session_id

    # ── Fase 1: httpx webapp API ──────────────────────────────────────────────
    try:
        import httpx
        async with httpx.AsyncClient(
            headers=_HEADERS,
            cookies=httpx_cookies,
            follow_redirects=True,
            timeout=SCRAPE_TIMEOUT,
        ) as client:
            tasks = [
                _search_via_webapp(client, q, reference, results, seen_urls)
                for q in queries
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(f"TikTok httpx: {len(results)} listing per {reference}")
    except Exception as e:
        logger.warning(f"TikTok httpx phase error: {e}")

    # ── Fase 2: Playwright fallback (sempre, per i hashtag più forti) ─────────
    # Usa solo i primi 2 hashtag per non esagerare con i browser headless
    playwright_tasks = [
        _search_via_playwright(reference, tag, results, seen_urls, session_id)
        for tag in hashtags[:2]
    ]
    try:
        await asyncio.gather(*playwright_tasks, return_exceptions=True)
    except Exception as e:
        logger.warning(f"TikTok Playwright phase error: {e}")

    # Deduplicazione finale per URL
    seen: set[str] = set()
    unique = [l for l in results if not (l.url in seen or seen.add(l.url))]  # type: ignore[func-returns-value]

    logger.info(f"TikTok: {len(unique)} listing unici per {reference}")
    return unique
