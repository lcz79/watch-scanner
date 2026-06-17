"""
BrandSpider: legge watchbase.com/{brand}/ e restituisce lista collezioni.
URL pattern: https://watchbase.com/{brand}/{collection}
"""
import logging, re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from config import BASE_URL
from fetcher import get_html

log = logging.getLogger("brand_spider")

_WATCHES_COUNT_RE = re.compile(r"watches(\d+)$")


def get_collections(brand_slug: str) -> list[dict]:
    """
    Legge watchbase.com/{brand_slug}/ e restituisce
    [{"name": str, "url": str, "slug": str, "count": int}]
    """
    url = f"{BASE_URL}/{brand_slug}/"
    html = get_html(url)
    if not html:
        log.warning(f"Brand non trovato: {brand_slug}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    collections = []
    seen_slugs: set[str] = set()

    for a in soup.select("a[href]"):
        href = a.get("href", "")
        parsed = urlparse(href)
        # path: /{brand}/{collection}  (es. /rolex/datejust)
        parts = [p for p in parsed.path.strip("/").split("/") if p]

        if len(parts) == 2 and parts[0] == brand_slug:
            col_slug = parts[1]
            if col_slug in seen_slugs:
                continue

            # Il testo del link spesso include il count: "Datejust 36 watches709"
            raw_text = a.get_text(strip=True)
            m = _WATCHES_COUNT_RE.search(raw_text)
            count = int(m.group(1)) if m else 0
            # Pulisci il nome dalla parte "watchesNNN"
            name = _WATCHES_COUNT_RE.sub("", raw_text).replace("watches", "").strip()
            if not name:
                name = col_slug.replace("-", " ").title()

            full_url = f"{BASE_URL}/{brand_slug}/{col_slug}"
            collections.append({
                "name": name,
                "url": full_url,
                "slug": col_slug,
                "count": count,
            })
            seen_slugs.add(col_slug)

    log.info(f"  {brand_slug}: {len(collections)} collezioni")
    return collections
