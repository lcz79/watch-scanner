"""
Cache in-memory dei risultati di scansione, con TTL breve.

Obiettivo: scollegare il costo della Scraping API dal numero di utenti senza
sacrificare la freschezza. La cache deduplica i picchi (tanti utenti sulla
stessa referenza in pochi minuti = una sola scansione live). Un cache MISS
esegue sempre una scansione fresca, e l'utente può forzare il refresh.
"""
import time
from threading import Lock

from models.schemas import ScanResult

# TTL breve: per un tool di caccia al prezzo la freschezza conta. 10 minuti.
TTL_SECONDS = 600
_MAX_ENTRIES = 500

_cache: dict[str, tuple[float, ScanResult]] = {}
_lock = Lock()


def _key(reference: str, max_price: float | None) -> str:
    return f"{(reference or '').strip().upper()}|{max_price or ''}"


def get(reference: str, max_price: float | None) -> tuple[float, ScanResult] | None:
    """Ritorna (timestamp_fetch, result) se in cache e non scaduto, altrimenti None."""
    k = _key(reference, max_price)
    with _lock:
        entry = _cache.get(k)
    if not entry:
        return None
    ts, result = entry
    if time.time() - ts > TTL_SECONDS:
        return None
    return ts, result


def put(reference: str, max_price: float | None, result: ScanResult) -> None:
    now = time.time()
    with _lock:
        _cache[_key(reference, max_price)] = (now, result)
        # pulizia leggera degli scaduti quando la cache cresce
        if len(_cache) > _MAX_ENTRIES:
            stale = [k for k, (t, _) in _cache.items() if now - t > TTL_SECONDS]
            for k in stale:
                _cache.pop(k, None)
