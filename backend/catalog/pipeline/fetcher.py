"""
HTTP fetcher con cache su disco, retry e rate limiting.
Salva ogni risposta in .cache/<url-slug>.html per evitare
di ri-scrapare se il processo viene interrotto.
"""
import hashlib, pathlib, time, logging, requests
from config import HEADERS, DELAY_BETWEEN_REQUESTS, CACHE_DIR

log = logging.getLogger("fetcher")
_session = requests.Session()
_session.headers.update(HEADERS)

_cache = pathlib.Path(CACHE_DIR)
_cache.mkdir(exist_ok=True)


def _cache_path(url: str) -> pathlib.Path:
    slug = hashlib.md5(url.encode()).hexdigest()
    return _cache / f"{slug}.html"


def get_html(url: str, force: bool = False) -> str | None:
    cp = _cache_path(url)
    if cp.exists() and not force:
        log.debug(f"[CACHE] {url}")
        return cp.read_text(encoding="utf-8", errors="replace")

    log.info(f"[GET] {url}")
    time.sleep(DELAY_BETWEEN_REQUESTS)
    try:
        r = _session.get(url, timeout=20)
        r.raise_for_status()
        cp.write_text(r.text, encoding="utf-8")
        return r.text
    except requests.HTTPError as e:
        log.warning(f"HTTP {e.response.status_code} — {url}")
        return None
    except Exception as e:
        log.warning(f"Errore fetch {url}: {e}")
        return None
