"""
HTTP fetcher con cache su disco e rate-limit handling intelligente.
Salva ogni risposta in .cache/<md5url>.html per non ri-scrapare se il processo
viene interrotto.

Rate limiting strategy:
  WatchBase consente ~100 req per burst; poi blocca per ~5 minuti.
  Alla prima 429 impostiamo un cooldown globale di 5 min e aspettiamo.
  Le request successive trovano il cooldown già attivo e attendono
  il residuo invece di ri-pagare la penalità completa.
"""
import hashlib, pathlib, time, logging, requests
from config import HEADERS, DELAY_BETWEEN_REQUESTS, CACHE_DIR

log = logging.getLogger("fetcher")
_session = requests.Session()
_session.headers.update(HEADERS)

_cache = pathlib.Path(CACHE_DIR)
_cache.mkdir(exist_ok=True)

_COOLDOWN_SECONDS = 300  # 5 min — tempo di cooldown dopo la prima 429
_rate_limited_until: float = 0.0   # timestamp fino a cui attendere


def _cache_path(url: str) -> pathlib.Path:
    slug = hashlib.md5(url.encode()).hexdigest()
    return _cache / f"{slug}.html"


def get_html(url: str, force: bool = False) -> str | None:
    global _rate_limited_until

    cp = _cache_path(url)
    if cp.exists() and not force:
        log.debug(f"[CACHE] {url}")
        return cp.read_text(encoding="utf-8", errors="replace")

    # Se siamo in cooldown, aspettiamo il residuo
    remaining = _rate_limited_until - time.time()
    if remaining > 0:
        log.warning(f"  [cooldown] attendo {remaining:.0f}s prima di {url}")
        time.sleep(remaining)

    log.info(f"[GET] {url}")
    time.sleep(DELAY_BETWEEN_REQUESTS)

    try:
        r = _session.get(url, timeout=30)
    except Exception as e:
        log.warning(f"Errore fetch {url}: {e}")
        return None

    if r.status_code in (429, 503):
        # Primo 429: impostiamo cooldown globale e facciamo un solo retry
        _rate_limited_until = time.time() + _COOLDOWN_SECONDS
        log.warning(
            f"  429/503 — rate limited. Cooldown {_COOLDOWN_SECONDS}s impostato. "
            f"Retry tra {_COOLDOWN_SECONDS}s..."
        )
        time.sleep(_COOLDOWN_SECONDS)
        try:
            r = _session.get(url, timeout=30)
        except Exception as e:
            log.warning(f"Errore fetch (retry) {url}: {e}")
            return None
        if r.status_code in (429, 503):
            log.warning(f"  429 ancora dopo cooldown — skip {url}")
            return None

    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        log.warning(f"HTTP {e.response.status_code} — {url}")
        return None

    cp.write_text(r.text, encoding="utf-8")
    return r.text
