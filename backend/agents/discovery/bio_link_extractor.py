"""
Bio Link Extractor.

Estrae URL da bio Instagram e risolve link aggregatori
(Linktree, Bento.me) per recuperare i link finali.
"""

import re

import httpx

from utils.logger import get_logger

logger = get_logger("discovery.bio_links")

# ---------------------------------------------------------------------------
# Pattern
# ---------------------------------------------------------------------------

URL_RE = re.compile(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+')
LINKTREE_RE = re.compile(r'linktr\.ee/(\w+)')
BENTO_RE = re.compile(r'bento\.me/(\w+)')

# Domini da escludere (social media)
SOCIAL_DOMAINS = {
    "instagram.com", "www.instagram.com",
    "facebook.com", "www.facebook.com",
    "tiktok.com", "www.tiktok.com",
    "youtube.com", "www.youtube.com",
    "twitter.com", "www.twitter.com",
    "x.com", "www.x.com",
}

_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8",
}

# ---------------------------------------------------------------------------
# Funzioni pubbliche
# ---------------------------------------------------------------------------


async def extract_links_from_bio(bio: str) -> list[str]:
    """
    Estrae tutti gli URL presenti nella bio, escludendo i social media.

    Args:
        bio: testo della bio Instagram.

    Returns:
        Lista di URL normalizzati (con schema https://).
    """
    if not bio:
        return []

    raw_urls = URL_RE.findall(bio)
    cleaned: list[str] = []

    for url in raw_urls:
        # Rimuovi punteggiatura finale spurea
        url = url.rstrip(".,;!?)")
        if not url.startswith("http"):
            url = "https://" + url
        if _is_social(url):
            continue
        cleaned.append(url)

    logger.debug(f"[bio_links] Trovati {len(cleaned)} URL nella bio")
    return cleaned


async def resolve_linktree(handle: str) -> list[str]:
    """
    Scarica la pagina linktr.ee/{handle} ed estrae tutti i link esterni.

    Args:
        handle: username Linktree (es. "watchmarket_it").

    Returns:
        Lista di URL esterni presenti nella pagina.
    """
    url = f"https://linktr.ee/{handle}"
    logger.debug(f"[linktree] Fetching {url}...")

    try:
        async with httpx.AsyncClient(
            headers=_HTTP_HEADERS,
            follow_redirects=True,
            timeout=10.0,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
    except httpx.HTTPStatusError as e:
        logger.warning(f"[linktree] HTTP {e.response.status_code} per {url}")
        return []
    except Exception as e:
        logger.warning(f"[linktree] Errore fetch {url}: {e}")
        return []

    # Estrai href da tag <a>
    href_re = re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\']', re.I)
    hrefs = href_re.findall(html)

    results: list[str] = []
    for href in hrefs:
        if href.startswith("http") and not _is_social(href) and "linktr.ee" not in href:
            results.append(href)

    # Dedup preservando ordine
    seen: set[str] = set()
    unique = [u for u in results if not (u in seen or seen.add(u))]  # type: ignore[func-returns-value]

    logger.debug(f"[linktree] @{handle} — {len(unique)} link estratti")
    return unique


async def resolve_bento(handle: str) -> list[str]:
    """
    Scarica la pagina bento.me/{handle} ed estrae link esterni.

    Args:
        handle: username Bento.me.

    Returns:
        Lista di URL esterni.
    """
    url = f"https://bento.me/{handle}"
    logger.debug(f"[bento] Fetching {url}...")

    try:
        async with httpx.AsyncClient(
            headers=_HTTP_HEADERS,
            follow_redirects=True,
            timeout=10.0,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
    except httpx.HTTPStatusError as e:
        logger.warning(f"[bento] HTTP {e.response.status_code} per {url}")
        return []
    except Exception as e:
        logger.warning(f"[bento] Errore fetch {url}: {e}")
        return []

    href_re = re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\']', re.I)
    hrefs = href_re.findall(html)

    results = [
        h for h in hrefs
        if h.startswith("http") and not _is_social(h) and "bento.me" not in h
    ]

    seen: set[str] = set()
    unique = [u for u in results if not (u in seen or seen.add(u))]  # type: ignore[func-returns-value]

    logger.debug(f"[bento] @{handle} — {len(unique)} link estratti")
    return unique


async def resolve_bio_links(bio: str) -> list[str]:
    """
    Entry point: estrae URL dalla bio, risolve aggregatori (Linktree, Bento),
    e ritorna la lista finale di URL concreti.

    Args:
        bio: testo della bio Instagram.

    Returns:
        Lista deduplicata di URL finali (esclusi social media).
    """
    if not bio:
        return []

    direct_links = await extract_links_from_bio(bio)
    all_links: list[str] = []

    for url in direct_links:
        lt_match = LINKTREE_RE.search(url)
        bento_match = BENTO_RE.search(url)

        if lt_match:
            handle = lt_match.group(1)
            resolved = await resolve_linktree(handle)
            if resolved:
                all_links.extend(resolved)
            else:
                # Fallback: tieni l'URL originale
                all_links.append(url)
        elif bento_match:
            handle = bento_match.group(1)
            resolved = await resolve_bento(handle)
            if resolved:
                all_links.extend(resolved)
            else:
                all_links.append(url)
        else:
            all_links.append(url)

    # Deduplication finale preservando ordine
    seen: set[str] = set()
    unique = [u for u in all_links if not (u in seen or seen.add(u))]  # type: ignore[func-returns-value]

    logger.info(f"[bio_links] resolve_bio_links — {len(unique)} URL finali")
    return unique


# ---------------------------------------------------------------------------
# Helper privato
# ---------------------------------------------------------------------------

def _is_social(url: str) -> bool:
    """True se l'URL appartiene a un dominio social da escludere."""
    try:
        # Estrae il dominio grezzo (dopo schema e prima del path)
        without_schema = url.split("://", 1)[-1]
        domain = without_schema.split("/")[0].lower()
        return domain in SOCIAL_DOMAINS
    except Exception:
        return False
