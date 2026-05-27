"""
Watch image resolver — fetches reference-specific watch images from Chrono24.
Caches results in memory to avoid repeated requests.
"""
import re
import httpx

_CACHE: dict[str, str] = {}

PLACEHOLDER = "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600&q=80&fit=crop"

_STATIC: dict[str, str] = {
    # Fallback static images for very common references
    "116610LN":   "https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=600&q=80&fit=crop",
    "116613LB":   "https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=600&q=80&fit=crop",
    "116500LN":   "https://images.unsplash.com/photo-1592652577702-e40b7ed85e5d?w=600&q=80&fit=crop",
    "5711/1A":    "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600&q=80&fit=crop",
    "5726/1A":    "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600&q=80&fit=crop",
    "5167A":      "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600&q=80&fit=crop",
    "15500ST":    "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=600&q=80&fit=crop",
    "6239":       "https://images.unsplash.com/photo-1495856458515-0637185db551?w=600&q=80&fit=crop",
    "6265":       "https://images.unsplash.com/photo-1495856458515-0637185db551?w=600&q=80&fit=crop",
    "16520":      "https://images.unsplash.com/photo-1495856458515-0637185db551?w=600&q=80&fit=crop",
    "126710BLNR": "https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=600&q=80&fit=crop",
    "RM 011":     "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=600&q=80&fit=crop",
}

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def get_watch_image(reference: str, brand: str = "", model: str = "") -> str:
    """Returns an image URL for the given reference. Uses cache."""
    if reference in _CACHE:
        return _CACHE[reference]

    if reference in _STATIC:
        _CACHE[reference] = _STATIC[reference]
        return _STATIC[reference]

    # Try Chrono24 og:image for reference page
    url = _try_chrono24(brand, reference)
    if not url:
        url = PLACEHOLDER

    _CACHE[reference] = url
    return url


def _try_chrono24(brand: str, reference: str) -> str | None:
    """Fetch og:image from Chrono24 search for the reference."""
    try:
        q = f"{brand} {reference}".strip()
        search_url = f"https://www.chrono24.com/search/index.htm?query={q}&dosearch=true&redirectToDetails=false"
        with httpx.Client(
            timeout=8,
            headers={"User-Agent": _UA, "Accept-Language": "en-US,en;q=0.9"},
            follow_redirects=True,
        ) as client:
            r = client.get(search_url)
            if r.status_code != 200:
                return None
            # og:image
            m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', r.text)
            if m:
                img = m.group(1)
                if "chrono24" in img or "unsplash" in img:
                    return img
            # Fallback: first article image in JSON-LD or data attrs
            m2 = re.search(r'"image"\s*:\s*"(https://img\.chrono24\.com/[^"]+)"', r.text)
            if m2:
                return m2.group(1)
    except Exception:
        pass
    return None
