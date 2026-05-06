"""
Bio Link Extractor Scraper per WatchScanner.

Sistema che:
  1. Legge la bio di ogni account reseller trovato via Instagram/TikTok/Facebook
  2. Estrae URL (diretti + aggregatori Linktree/Bento)
  3. Scrapa il sito web del reseller cercando la referenza
  4. Ritorna WatchListing se trovata con prezzo

Basa il proprio funzionamento su agents/discovery/bio_link_extractor.py
(che gestisce estrazione URL e risoluzione aggregatori) ed aggiunge
lo scraping effettivo del sito web del reseller.

Uso:
  from scrapers.bio_link_extractor import scrape_reseller_bio
  listings = await scrape_reseller_bio(
      username="watchmarket_it",
      bio="Reseller Rolex autorizzato. Link: linktr.ee/watchmarket_it",
      reference="116610LN",
  )
"""

import asyncio
import re
from datetime import datetime
from bs4 import BeautifulSoup
import httpx
from utils.logger import get_logger
from models.schemas import WatchListing
from agents.discovery.bio_link_extractor import resolve_bio_links

logger = get_logger("scraper.bio_link")

# ── Costanti ─────────────────────────────────────────────────────────────────

SCRAPE_TIMEOUT = 30.0  # secondi httpx
MAX_PAGES_PER_SITE = 3   # max pagine da scrapare per sito reseller
MAX_URLS_PER_RESELLER = 3  # max URL da provare per reseller

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8",
}

# ── Import regex comuni dall'OCR per consistenza ──────────────────────────────

from scrapers.stories.ocr import (
    _parse_price,
    _detect_reference,
    _detect_brand,
    _detect_condition,
    _is_watch_related,
    BRAND_KEYWORDS,
)

# ── Pattern per trovare pagine prodotto su siti reseller ─────────────────────

# Parole chiave che indicano una pagina prodotto/listing
PRODUCT_PAGE_SIGNALS = [
    "product", "prodotto", "watch", "orologio", "listing", "detail",
    "item", "shop", "store", "negozio", "vendita",
]

# Estensioni da evitare (non sono pagine prodotto)
_SKIP_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".css", ".js"}


# ── Scraping sito web ─────────────────────────────────────────────────────────

def _extract_text_from_html(html: str) -> str:
    """Estrae il testo visibile da una pagina HTML."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        # Rimuovi script, style, nav e footer
        for tag in soup(["script", "style", "nav", "footer", "header", "meta"]):
            tag.decompose()
        return " ".join(soup.get_text(" ", strip=True).split())
    except Exception:
        return ""


def _find_product_links(html: str, base_url: str, reference: str) -> list[str]:
    """
    Estrae link a pagine prodotto dal sito che potrebbero contenere la referenza.
    Priorità a link che contengono la referenza nell'URL.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        ref_clean = reference.replace("/", "").replace(" ", "").lower()
        ref_parts = re.findall(r'[a-z0-9]+', reference.lower())

        product_links: list[str] = []
        fallback_links: list[str] = []

        from urllib.parse import urljoin, urlparse

        for a_tag in soup.find_all("a", href=True):
            href = str(a_tag["href"]).strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue

            # Costruisci URL assoluto
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            # Rimani sullo stesso dominio
            base_domain = urlparse(base_url).netloc
            if parsed.netloc and parsed.netloc != base_domain:
                continue

            # Salta estensioni non-HTML
            path_lower = parsed.path.lower()
            if any(path_lower.endswith(ext) for ext in _SKIP_EXTENSIONS):
                continue

            path_and_query = (parsed.path + "?" + parsed.query).lower()

            # Link che contiene la referenza → priorità massima
            if ref_clean in path_and_query or any(p in path_and_query for p in ref_parts if len(p) >= 4):
                product_links.append(full_url)
            # Link che sembra una pagina prodotto → fallback
            elif any(sig in path_and_query for sig in PRODUCT_PAGE_SIGNALS):
                fallback_links.append(full_url)

        # Deduplicazione
        all_links = list(dict.fromkeys(product_links + fallback_links))
        return all_links[:MAX_PAGES_PER_SITE]

    except Exception as e:
        logger.debug(f"find_product_links error: {e}")
        return []


async def _scrape_page(
    client: httpx.AsyncClient,
    url: str,
    reference: str,
) -> WatchListing | None:
    """
    Scarica una singola pagina e verifica se contiene un listing valido
    per la referenza specificata.
    """
    try:
        resp = await client.get(url, timeout=SCRAPE_TIMEOUT)
        if resp.status_code != 200:
            return None
        html = resp.text
    except Exception as e:
        logger.debug(f"Fetch error {url}: {e}")
        return None

    text = _extract_text_from_html(html)
    if not text:
        return None

    # Verifica che la pagina sia orologio-related
    if not _is_watch_related(text):
        return None

    # Verifica presenza referenza
    ref_clean = reference.replace(" ", "").upper()
    if ref_clean not in text.upper() and reference.upper() not in text.upper():
        # Tenta comunque se c'è un prezzo plausibile con brand corretto
        price = _parse_price(text)
        brand = _detect_brand(text)
        if not price or not brand:
            return None

    # Estrai prezzo (obbligatorio)
    price = _parse_price(text)
    if not price:
        return None

    # Estrai altri campi
    detected_ref = _detect_reference(text) or reference
    brand = _detect_brand(text)
    condition = _detect_condition(text)

    # Nome venditore dall'URL
    from urllib.parse import urlparse
    seller_domain = urlparse(url).netloc.replace("www.", "")

    logger.info(f"Bio link MATCH: {seller_domain} → {detected_ref} {price}€")

    return WatchListing(
        source="reseller_website",
        reference=detected_ref,
        price=price,
        currency="EUR",
        seller=seller_domain,
        url=url,
        condition=condition,
        scraped_at=datetime.now(),
        description=text[:200],
        image_url=None,
    )


async def _scrape_reseller_site(
    site_url: str,
    reference: str,
) -> list[WatchListing]:
    """
    Scrapa un sito web reseller cercando la referenza.

    Strategia:
      1. Scarica homepage
      2. Cerca link a pagine prodotto (specialmente con la referenza nell'URL)
      3. Prova la ricerca interna /search?q=<referenza>
      4. Scrapa ogni pagina trovata
    """
    results: list[WatchListing] = []
    from urllib.parse import urljoin, urlencode

    async with httpx.AsyncClient(
        headers=_HEADERS,
        follow_redirects=True,
        timeout=SCRAPE_TIMEOUT,
    ) as client:
        # Step 1: homepage o search diretta
        search_url = urljoin(site_url, f"/search?q={reference.replace(' ', '+')}")
        urls_to_try = [
            search_url,
            urljoin(site_url, f"/?s={reference.replace(' ', '+')}"),
            urljoin(site_url, f"/products?q={reference.replace(' ', '+')}"),
            site_url,
        ]

        product_urls: list[str] = []

        for try_url in urls_to_try[:2]:
            try:
                resp = await client.get(try_url, timeout=15.0)
                if resp.status_code != 200:
                    continue
                html = resp.text

                # Controlla subito se questa pagina contiene il listing
                listing = await _scrape_page(client, try_url, reference)
                if listing:
                    results.append(listing)
                    return results  # Trovato! Basta così

                # Trova link prodotto da esplorare
                found = _find_product_links(html, site_url, reference)
                product_urls.extend(found)
            except Exception as e:
                logger.debug(f"Site search error {try_url}: {e}")

        # Step 2: scrapa le pagine prodotto trovate
        product_urls = list(dict.fromkeys(product_urls))[:MAX_PAGES_PER_SITE]
        for prod_url in product_urls:
            listing = await _scrape_page(client, prod_url, reference)
            if listing:
                results.append(listing)
            await asyncio.sleep(0.5)  # cortesia verso il server

    return results


# ── Entry point principale ────────────────────────────────────────────────────

async def scrape_reseller_bio(
    username: str,
    bio: str,
    reference: str,
) -> list[WatchListing]:
    """
    Punto di ingresso principale: dato un reseller con la sua bio e una referenza,
    estrae URL dalla bio, risolve aggregatori, scrapa i siti trovati.

    Args:
        username:  handle del reseller (es. "watchmarket_it")
        bio:       testo della bio Instagram/TikTok
        reference: referenza orologio da cercare (es. "116610LN")

    Returns:
        Lista di WatchListing con source="reseller_website"
    """
    results: list[WatchListing] = []

    if not bio:
        logger.debug(f"@{username}: bio vuota — skip")
        return results

    logger.info(f"@{username}: analisi bio per {reference}")

    # Risolvi URL dalla bio (gestisce Linktree, Bento, URL diretti)
    try:
        site_urls = await resolve_bio_links(bio)
    except Exception as e:
        logger.warning(f"@{username} bio link resolve error: {e}")
        return results

    if not site_urls:
        logger.debug(f"@{username}: nessun URL trovato in bio")
        return results

    logger.info(f"@{username}: trovati {len(site_urls)} URL da esplorare")

    # Scrapa ogni sito (max MAX_URLS_PER_RESELLER)
    tasks = [
        _scrape_reseller_site(url, reference)
        for url in site_urls[:MAX_URLS_PER_RESELLER]
    ]
    task_results = await asyncio.gather(*tasks, return_exceptions=True)

    for res in task_results:
        if isinstance(res, list):
            results.extend(res)
        elif isinstance(res, Exception):
            logger.debug(f"@{username} site scrape error: {res}")

    logger.info(f"@{username}: {len(results)} listing dal sito web per {reference}")
    return results


async def scrape_resellers_batch(
    resellers: list[dict],
    reference: str,
    max_concurrent: int = 3,
) -> list[WatchListing]:
    """
    Scrapa bio link di una lista di reseller in parallelo (con semaforo per concorrenza).

    Args:
        resellers:       lista di dict con campi "username" e "bio"
        reference:       referenza da cercare
        max_concurrent:  numero massimo di reseller da processare in parallelo

    Returns:
        Lista aggregata di WatchListing
    """
    results: list[WatchListing] = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _bounded_scrape(reseller: dict) -> list[WatchListing]:
        async with semaphore:
            return await scrape_reseller_bio(
                username=reseller.get("username", "unknown"),
                bio=reseller.get("bio", ""),
                reference=reference,
            )

    tasks = [_bounded_scrape(r) for r in resellers]
    task_results = await asyncio.gather(*tasks, return_exceptions=True)

    for res in task_results:
        if isinstance(res, list):
            results.extend(res)

    logger.info(f"Bio link batch: {len(results)} listing totali per {reference} ({len(resellers)} reseller)")
    return results
