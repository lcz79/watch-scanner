"""
Website Crawler Agent.

Analizza siti web di reseller per rilevare se sono ecommerce di orologi,
identificare il CMS usato, e raccogliere link a pagine prodotto.

Crawla homepage + fino a 3 pagine interne e aggiorna il DB dei dealer
con cms_type e last_crawled.
"""

import asyncio
from datetime import datetime
from urllib.parse import urlparse, urljoin, urldefrag

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger
from agents.discovery import resellers_db as db_module

logger = get_logger("discovery.website_crawler")

# ── Costanti ──────────────────────────────────────────────────────────────────

CMS_SIGNATURES: dict[str, list[str]] = {
    "shopify": ["cdn.shopify.com", "myshopify.com", "Shopify.theme"],
    "woocommerce": ["woocommerce", "wc-", "/wp-content/"],
    "prestashop": ["prestashop", "/modules/"],
    "magento": ["Magento", "mage/"],
    "custom": [],
}

WATCH_KEYWORDS: list[str] = [
    "rolex", "patek", "audemars", "omega", "watches", "orologi",
    "daytona", "submariner", "nautilus", "royal oak", "tudor",
    "iwc", "breitling", "hublot", "cartier", "richard mille",
    "timepiece", "chronograph", "orologio", "montres",
]

PRODUCT_SELECTORS: list[str] = [
    ".product",
    ".woocommerce-loop-product",
    ".product-item",
    "[class*='product-card']",
    "[class*='item-card']",
    "article.post-type-product",
    ".product-grid",
    ".product-list",
    "[class*='product-tile']",
    "[data-product-id]",
    "[data-product]",
]

# Pagine interne da cercare prioritariamente
PRIORITY_PATHS: list[str] = [
    "/shop", "/store", "/watches", "/orologi", "/catalog",
    "/prodotti", "/products", "/collection", "/collections",
    "/buy", "/acquista", "/vendita", "/shop/watches",
]

REQUEST_TIMEOUT = 15.0  # secondi

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ── Funzioni principali ───────────────────────────────────────────────────────

async def detect_cms(html: str, url: str) -> str:
    """
    Analizza l'HTML e l'URL per rilevare il CMS usato.
    Ritorna il nome del CMS o 'unknown'.
    """
    combined = html + url

    for cms_name, signatures in CMS_SIGNATURES.items():
        if cms_name == "custom":
            continue
        if any(sig in combined for sig in signatures):
            return cms_name

    return "unknown"


async def is_watch_dealer_site(html: str) -> bool:
    """
    Ritorna True se il sito contiene keyword di orologi
    e almeno un selettore CSS tipico di pagine prodotto.
    """
    html_lower = html.lower()

    # Verifica presenza keyword orologi
    keyword_hits = sum(1 for kw in WATCH_KEYWORDS if kw in html_lower)
    if keyword_hits < 2:
        return False

    # Verifica presenza elementi prodotto
    soup = BeautifulSoup(html, "html.parser")
    for selector in PRODUCT_SELECTORS:
        if soup.select(selector):
            return True

    # Fallback: almeno 3 keyword + tag <article> o <section> con contenuto
    if keyword_hits >= 3:
        articles = soup.find_all(["article", "section"])
        if articles:
            return True

    return False


async def extract_outbound_links(html: str, base_url: str) -> list[str]:
    """
    Estrae link esterni (con dominio diverso dal dominio base).
    Ritorna lista di URL assoluti deduplicati.
    """
    base_domain = urlparse(base_url).netloc.lower().lstrip("www.")
    soup = BeautifulSoup(html, "html.parser")
    outbound: set[str] = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        absolute = urljoin(base_url, href)
        absolute, _ = urldefrag(absolute)

        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue

        link_domain = parsed.netloc.lower().lstrip("www.")
        if link_domain and link_domain != base_domain:
            outbound.add(absolute)

    return sorted(outbound)


async def _fetch_page(client: httpx.AsyncClient, url: str) -> tuple[str | None, str]:
    """
    Scarica una pagina HTTP e ritorna (html, url_finale_dopo_redirect).
    Ritorna (None, url) in caso di errore.
    """
    try:
        response = await client.get(url, follow_redirects=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "text/plain" not in content_type:
            return None, str(response.url)
        return response.text, str(response.url)
    except httpx.TimeoutException:
        logger.warning(f"Timeout su {url}")
        return None, url
    except httpx.HTTPStatusError as e:
        logger.debug(f"HTTP {e.response.status_code} su {url}")
        return None, url
    except httpx.ConnectError:
        logger.warning(f"Connessione fallita su {url}")
        return None, url
    except Exception as e:
        logger.debug(f"Errore generico su {url}: {e}")
        return None, url


def _extract_internal_links(html: str, base_url: str) -> list[str]:
    """
    Estrae link interni (stesso dominio) dalla pagina.
    Privilegia URL che sembrano pagine prodotto/shop.
    """
    base_domain = urlparse(base_url).netloc.lower()
    soup = BeautifulSoup(html, "html.parser")
    internal: dict[str, int] = {}  # url -> priority score

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        absolute = urljoin(base_url, href)
        absolute, _ = urldefrag(absolute)

        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc.lower() != base_domain:
            continue
        if absolute == base_url:
            continue

        # Calcola priorità in base al path
        path_lower = parsed.path.lower()
        priority = 0
        for prio_path in PRIORITY_PATHS:
            if prio_path in path_lower:
                priority += 10
                break
        for kw in WATCH_KEYWORDS:
            if kw in path_lower:
                priority += 5
                break

        if absolute not in internal or internal[absolute] < priority:
            internal[absolute] = priority

    # Ordina per priorità decrescente
    return [url for url, _ in sorted(internal.items(), key=lambda x: x[1], reverse=True)]


def _find_keywords_in_html(html: str) -> list[str]:
    """Ritorna le keyword di orologi trovate nell'HTML."""
    html_lower = html.lower()
    return [kw for kw in WATCH_KEYWORDS if kw in html_lower]


async def crawl_website(url: str) -> dict:
    """
    Crawla homepage + fino a 3 pagine interne del sito.

    Ritorna:
    {
        "url": str,
        "cms_type": str,
        "is_dealer": bool,
        "product_pages": list[str],
        "outbound_links": list[str],
        "watch_keywords_found": list[str],
        "error": str | None,
    }
    """
    result: dict = {
        "url": url,
        "cms_type": "unknown",
        "is_dealer": False,
        "product_pages": [],
        "outbound_links": [],
        "watch_keywords_found": [],
        "error": None,
    }

    # Normalizza URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        result["url"] = url

    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
        verify=False,  # tolera SSL self-signed
        timeout=REQUEST_TIMEOUT,
    ) as client:

        # --- 1. Scarica homepage ---
        homepage_html, final_url = await _fetch_page(client, url)
        if homepage_html is None:
            # Prova con http:// se https fallisce
            if url.startswith("https://"):
                fallback_url = "http://" + url[8:]
                homepage_html, final_url = await _fetch_page(client, fallback_url)

        if homepage_html is None:
            result["error"] = "impossibile caricare homepage"
            logger.warning(f"Crawl fallito per {url}: homepage irraggiungibile")
            return result

        result["url"] = final_url
        all_html = homepage_html

        # CMS e keyword dalla homepage
        result["cms_type"] = await detect_cms(homepage_html, final_url)
        result["watch_keywords_found"] = _find_keywords_in_html(homepage_html)
        result["outbound_links"] = await extract_outbound_links(homepage_html, final_url)

        # --- 2. Crawla fino a 3 pagine interne ---
        internal_candidates = _extract_internal_links(homepage_html, final_url)
        visited: set[str] = {final_url}
        pages_crawled = 0

        for candidate_url in internal_candidates:
            if pages_crawled >= 3:
                break
            if candidate_url in visited:
                continue
            visited.add(candidate_url)

            page_html, page_final_url = await _fetch_page(client, candidate_url)
            if page_html is None:
                continue

            pages_crawled += 1
            all_html += page_html

            # Aggiorna keyword trovate
            page_keywords = _find_keywords_in_html(page_html)
            for kw in page_keywords:
                if kw not in result["watch_keywords_found"]:
                    result["watch_keywords_found"].append(kw)

            # Se la pagina ha elementi prodotto, la registra come product_page
            soup = BeautifulSoup(page_html, "html.parser")
            for selector in PRODUCT_SELECTORS:
                if soup.select(selector):
                    result["product_pages"].append(page_final_url)
                    break

            # Breve pausa per non sovraccaricare il server
            await asyncio.sleep(1.0)

        # --- 3. Determina se è un dealer di orologi ---
        result["is_dealer"] = await is_watch_dealer_site(all_html)

        # --- 4. Aggiorna DB del dealer ---
        _update_dealer_in_db(result)

    logger.info(
        f"Crawl OK: {result['url']} | CMS={result['cms_type']} | "
        f"dealer={result['is_dealer']} | "
        f"kw={result['watch_keywords_found'][:3]} | "
        f"product_pages={len(result['product_pages'])}"
    )
    return result


def _update_dealer_in_db(crawl_result: dict):
    """
    Aggiorna il record del dealer nel DB con cms_type e last_crawled.
    Se non esiste ancora nel DB, non lo crea (quella responsabilità
    spetta a web_expansion.py o agli altri discovery agent).
    """
    try:
        db = db_module.load()
        url = crawl_result["url"]
        domain = urlparse(url).netloc.lower()

        # Cerca per dominio tra i reseller esistenti
        for username, info in db["resellers"].items():
            website = info.get("website", "")
            if not website:
                continue
            existing_domain = urlparse(website).netloc.lower()
            if existing_domain == domain:
                info["cms_type"] = crawl_result["cms_type"]
                info["last_crawled"] = datetime.now().isoformat()
                info["is_dealer_confirmed"] = crawl_result["is_dealer"]
                info["product_pages"] = crawl_result["product_pages"][:10]
                db_module.save(db)
                logger.debug(f"DB aggiornato per {domain}: cms={crawl_result['cms_type']}")
                return

        logger.debug(f"Dominio {domain} non trovato nel DB reseller, skip aggiornamento")
    except Exception as e:
        logger.error(f"Errore aggiornamento DB per {crawl_result['url']}: {e}")


# ── CLI per test rapido ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.watchfinder.co.uk"

    async def main():
        result = await crawl_website(test_url)
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))

    asyncio.run(main())
