"""
Web Expansion Agent.

Trova nuovi dealer di orologi tramite:
  1. Ricerche su DuckDuckGo HTML (no JS, no API key necessaria)
  2. Analisi dei link esterni presenti nei siti dei dealer già noti

Per ogni nuovo URL trovato: crawl base + se sembra dealer → aggiunta al DB.
"""

import asyncio
from datetime import datetime
from urllib.parse import urlparse, urlencode, quote_plus

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger
from agents.discovery import resellers_db as db_module
from agents.discovery.website_crawler import (
    crawl_website,
    extract_outbound_links,
    _fetch_page,
)

logger = get_logger("discovery.web_expansion")

# ── Costanti ──────────────────────────────────────────────────────────────────

SEARCH_QUERIES: list[str] = [
    "rolex dealer italy buy online",
    "luxury watch reseller italia",
    "orologi usati vendita online",
    "buy patek philippe dealer europe",
    "rivenditore rolex usato italia",
    "vendita orologi lusso online shop",
    "independent watch dealer italy",
    "orologi vintage vendita online",
    "buy audemars piguet dealer europe",
    "omega rolex tudor shop online italy",
]

EXCLUDED_DOMAINS: set[str] = {
    "instagram.com", "www.instagram.com",
    "facebook.com", "www.facebook.com",
    "ebay.com", "www.ebay.com",
    "ebay.it", "www.ebay.it",
    "amazon.com", "www.amazon.com",
    "amazon.it", "www.amazon.it",
    "chrono24.com", "www.chrono24.com",
    "chrono24.it", "www.chrono24.it",
    "watchfinder.com", "www.watchfinder.com",
    "subito.it", "www.subito.it",
    "idealista.it", "www.idealista.it",
    "wikipedia.org", "www.wikipedia.org",
    "youtube.com", "www.youtube.com",
    "twitter.com", "www.twitter.com",
    "x.com", "www.x.com",
    "tiktok.com", "www.tiktok.com",
    "linkedin.com", "www.linkedin.com",
    "reddit.com", "www.reddit.com",
    "pinterest.com", "www.pinterest.com",
    "trustpilot.com", "www.trustpilot.com",
    "google.com", "www.google.com",
    "bing.com", "www.bing.com",
    "yahoo.com", "www.yahoo.com",
    "duckduckgo.com", "www.duckduckgo.com",
    "vinted.it", "www.vinted.it",
    "vinted.com", "www.vinted.com",
    "catawiki.com", "www.catawiki.com",
    "sothebys.com", "www.sothebys.com",
    "christies.com", "www.christies.com",
    "watchbox.com", "www.watchbox.com",
    "hodinkee.com", "www.hodinkee.com",
    "fratellowatches.com", "www.fratellowatches.com",
}

DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://duckduckgo.com/",
}

REQUEST_TIMEOUT = 15.0
DELAY_BETWEEN_SEARCHES = 4.0   # secondi tra una query e l'altra
DELAY_BETWEEN_CRAWLS = 3.0     # secondi tra un crawl e l'altro


# ── Funzioni principali ───────────────────────────────────────────────────────

async def search_duckduckgo(query: str, num_results: int = 10) -> list[str]:
    """
    Cerca su DuckDuckGo HTML (https://html.duckduckgo.com/html/?q=query).
    Estrae URL dai risultati organici. Usa httpx, non richiede JS.
    Ritorna lista di URL assoluti (deduplicati).
    """
    params = {"q": query, "kl": "it-it"}
    search_url = DUCKDUCKGO_HTML_URL + "?" + urlencode(params)

    try:
        async with httpx.AsyncClient(
            headers=HEADERS,
            follow_redirects=True,
            timeout=REQUEST_TIMEOUT,
        ) as client:
            response = await client.post(
                DUCKDUCKGO_HTML_URL,
                data={"q": query, "kl": "it-it"},
                headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            html = response.text

    except httpx.TimeoutException:
        logger.warning(f"DuckDuckGo timeout per query: {query!r}")
        return []
    except httpx.HTTPStatusError as e:
        logger.warning(f"DuckDuckGo HTTP {e.response.status_code} per query: {query!r}")
        return []
    except Exception as e:
        logger.error(f"DuckDuckGo errore per query {query!r}: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    seen: set[str] = set()

    # I risultati DuckDuckGo HTML sono in <a class="result__url"> o <a class="result__a">
    for tag in soup.select("a.result__a, a.result__url, .result__extras__url"):
        href = tag.get("href", "").strip()
        if not href:
            continue

        # DDG a volte usa redirect interni tipo //duckduckgo.com/l/?uddg=...
        if "duckduckgo.com/l/" in href:
            # Estrai uddg parameter
            from urllib.parse import parse_qs, urlparse as _up
            parsed = _up(href)
            qs = parse_qs(parsed.query)
            uddg = qs.get("uddg", [None])[0]
            if uddg:
                href = uddg

        if not href.startswith(("http://", "https://")):
            continue

        parsed = urlparse(href)
        domain = parsed.netloc.lower()
        if domain in EXCLUDED_DOMAINS:
            continue
        if href in seen:
            continue
        seen.add(href)

        # Normalizza a homepage se il path è troppo profondo (>2 livelli)
        path_parts = [p for p in parsed.path.split("/") if p]
        if len(path_parts) > 2:
            href = f"{parsed.scheme}://{parsed.netloc}/"

        if href not in seen:
            seen.add(href)
            urls.append(href)

        if len(urls) >= num_results:
            break

    logger.info(f"DuckDuckGo '{query}': {len(urls)} URL trovati")
    return urls


async def filter_dealer_domains(urls: list[str]) -> list[str]:
    """
    Filtra una lista di URL:
    - Esclude social media e marketplace noti
    - Esclude URL con path troppo specifici (articoli di blog, ecc.)
    - Normalizza a homepage
    - Deduplicata per dominio
    Ritorna solo siti che potrebbero essere reseller indipendenti.
    """
    seen_domains: set[str] = set()
    filtered: list[str] = []

    for url in urls:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        bare_domain = domain.lstrip("www.")

        # Escludi domini nella blacklist
        if domain in EXCLUDED_DOMAINS or bare_domain in EXCLUDED_DOMAINS:
            continue

        # Escludi domini già visti (dedup per dominio)
        if domain in seen_domains:
            continue
        seen_domains.add(domain)

        # Normalizza a homepage
        homepage = f"{parsed.scheme}://{domain}/"
        filtered.append(homepage)

    return filtered


async def expand_from_outbound_links(dealer_urls: list[str]) -> list[str]:
    """
    Dati URL di dealer noti, scarica le loro homepage ed estrae
    i link esterni. Ritorna i nuovi URL candidati (filtrati).
    """
    all_outbound: set[str] = set()

    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
        verify=False,
        timeout=REQUEST_TIMEOUT,
    ) as client:
        for url in dealer_urls:
            html, final_url = await _fetch_page(client, url)
            if html is None:
                continue

            outbound = await extract_outbound_links(html, final_url)
            for link in outbound:
                parsed = urlparse(link)
                domain = parsed.netloc.lower()
                bare = domain.lstrip("www.")
                if domain not in EXCLUDED_DOMAINS and bare not in EXCLUDED_DOMAINS:
                    # Normalizza a homepage
                    homepage = f"{parsed.scheme}://{domain}/"
                    all_outbound.add(homepage)

            await asyncio.sleep(1.5)

    candidates = await filter_dealer_domains(list(all_outbound))
    logger.info(f"expand_from_outbound_links: {len(candidates)} candidati da {len(dealer_urls)} dealer")
    return candidates


def _add_website_dealer_to_db(
    db: dict,
    url: str,
    crawl_result: dict,
) -> bool:
    """
    Aggiunge un nuovo dealer website al DB dei reseller.
    Ritorna True se è stato effettivamente aggiunto (nuovo), False altrimenti.
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    bare_domain = domain.lstrip("www.")

    # Controlla se il dominio esiste già (per username o per campo website)
    for username, info in db["resellers"].items():
        existing_website = info.get("website", "")
        if existing_website:
            existing_domain = urlparse(existing_website).netloc.lower()
            if existing_domain == domain or existing_domain.lstrip("www.") == bare_domain:
                logger.debug(f"Dominio {domain} già nel DB come @{username}")
                return False

    # Usa il dominio come username sintetico per siti web
    synthetic_username = f"web:{bare_domain}"

    if db_module.is_known(db, synthetic_username):
        return False

    # Score base: se è confermato dealer +5, per ogni keyword +1
    score = 0
    reasons: list[str] = []

    if crawl_result.get("is_dealer"):
        score += 5
        reasons.append("is_dealer=True")

    kw_found = crawl_result.get("watch_keywords_found", [])
    kw_score = min(len(kw_found), 3)
    score += kw_score
    if kw_found:
        reasons.append(f"keywords: {kw_found[:3]}")

    cms = crawl_result.get("cms_type", "unknown")
    if cms in ("shopify", "woocommerce", "prestashop", "magento"):
        score += 1
        reasons.append(f"cms={cms}")

    product_pages = crawl_result.get("product_pages", [])
    if product_pages:
        score += 1
        reasons.append(f"{len(product_pages)} product pages")

    if score < db_module.MIN_SCORE:
        logger.debug(f"Score {score} troppo basso per {domain}, skip")
        return False

    db["resellers"][synthetic_username] = {
        "username": synthetic_username,
        "platform": "website",
        "score": score,
        "reasons": reasons,
        "followers": 0,
        "bio": "",
        "pk": "",
        "website": url,
        "cms_type": cms,
        "watch_keywords_found": kw_found,
        "product_pages": product_pages[:10],
        "discovered_via": "web_expansion",
        "discovered_at": datetime.now().isoformat(),
        "last_crawled": datetime.now().isoformat(),
    }
    db["stats"]["website"] = db["stats"].get("website", 0) + 1
    logger.info(f"  + nuovo dealer web: {url} | score={score} | {reasons[:2]}")
    return True


async def run_web_expansion() -> list[str]:
    """
    Entry point principale del Web Expansion Agent.

    Esegue:
    1. Ricerche DuckDuckGo per tutte le SEARCH_QUERIES
    2. Filtraggio e deduplicazione degli URL trovati
    3. Crawl di ogni URL candidato
    4. Aggiunta al DB dei dealer confermati
    5. Espansione tramite link esterni dei dealer noti

    Ritorna lista di nuovi domini scoperti in questa sessione.
    """
    logger.info("=== Web Expansion avviata ===")
    db = db_module.load()
    new_domains: list[str] = []
    all_candidates: set[str] = set()

    # --- Fase 1: DuckDuckGo search ---
    logger.info(f"Fase 1: ricerche DuckDuckGo ({len(SEARCH_QUERIES)} query)")
    for i, query in enumerate(SEARCH_QUERIES):
        urls = await search_duckduckgo(query, num_results=10)
        filtered = await filter_dealer_domains(urls)
        for url in filtered:
            all_candidates.add(url)
        if i < len(SEARCH_QUERIES) - 1:
            await asyncio.sleep(DELAY_BETWEEN_SEARCHES)

    logger.info(f"Fase 1 completata: {len(all_candidates)} candidati unici")

    # --- Fase 2: Espansione da dealer noti nel DB ---
    logger.info("Fase 2: espansione da dealer noti nel DB")
    known_websites = [
        info.get("website", "")
        for info in db["resellers"].values()
        if info.get("website") and info.get("platform") == "website"
    ]
    if known_websites:
        extra_candidates = await expand_from_outbound_links(known_websites[:20])
        for url in extra_candidates:
            all_candidates.add(url)
        logger.info(f"Fase 2 completata: {len(extra_candidates)} candidati aggiuntivi")
    else:
        logger.info("Fase 2: nessun dealer web noto nel DB, skip")

    # --- Fase 3: Crawl e classificazione ---
    logger.info(f"Fase 3: crawl di {len(all_candidates)} candidati")

    # Escludi URL già nel DB
    already_known_domains = set()
    for info in db["resellers"].values():
        website = info.get("website", "")
        if website:
            already_known_domains.add(urlparse(website).netloc.lower())

    to_crawl = []
    for url in all_candidates:
        domain = urlparse(url).netloc.lower()
        if domain not in already_known_domains:
            to_crawl.append(url)

    logger.info(f"Da crawlare (esclusi già noti): {len(to_crawl)}")

    for i, url in enumerate(to_crawl):
        logger.debug(f"Crawling [{i+1}/{len(to_crawl)}]: {url}")
        try:
            crawl_result = await crawl_website(url)

            if crawl_result.get("is_dealer"):
                added = _add_website_dealer_to_db(db, crawl_result["url"], crawl_result)
                if added:
                    new_domains.append(crawl_result["url"])
                    db_module.save(db)
            else:
                logger.debug(f"Non dealer: {url}")

        except Exception as e:
            logger.error(f"Errore crawl {url}: {e}")

        if i < len(to_crawl) - 1:
            await asyncio.sleep(DELAY_BETWEEN_CRAWLS)

    # --- Salvataggio finale ---
    db_module.save(db)

    logger.info(
        f"=== Web Expansion completata | "
        f"Crawlati: {len(to_crawl)} | "
        f"Nuovi dealer: {len(new_domains)} ==="
    )
    return new_domains


# ── CLI per test rapido ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    async def main():
        if len(sys.argv) > 1 and sys.argv[1] == "search":
            query = " ".join(sys.argv[2:]) or "rolex dealer italy buy online"
            urls = await search_duckduckgo(query, num_results=10)
            print(f"Risultati per '{query}':")
            for u in urls:
                print(f"  {u}")
        elif len(sys.argv) > 1 and sys.argv[1] == "crawl":
            url = sys.argv[2]
            from agents.discovery.website_crawler import crawl_website
            result = await crawl_website(url)
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            new = await run_web_expansion()
            print(f"\nNuovi dealer scoperti ({len(new)}):")
            for d in new:
                print(f"  {d}")

    asyncio.run(main())
