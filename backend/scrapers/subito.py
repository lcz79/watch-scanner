"""
Scraper per subito.it — usa l'API Hades interna (stessa usata dal sito).
Endpoint: https://www.subito.it/hades/v1/search/items

Miglioramenti rispetto alla versione originale:
- URL diretto categoria "Orologi da polso" (cat=28)
- Filtro categoria a livello API (evita risultati di altre categorie)
- Estrazione condizione ("Usato", "Nuovo", ecc.)
- Paginazione: fino a 3 pagine (120 annunci)
"""
import httpx
import re
from datetime import datetime
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing

logger = get_logger("scraper.subito")

_HADES_URL = "https://www.subito.it/hades/v1/search/items"

# URL di priming HTML — usa la categoria specifica orologi da polso
# cat=28 → "Orologi da polso" dentro "Orologi e Gioielli"
_PRIME_URL = "https://www.subito.it/orologi-e-gioielli/orologi-da-polso/"

# Quante pagine raccogliere (ogni pagina = 40 annunci → 3 pag = 120 max)
_MAX_PAGES = 3
_PAGE_SIZE = 40

# Mappatura condizione dal campo Hades "type" o dalla feature "condition"
_CONDITION_MAP = {
    "new": "new",
    "nuovo": "new",
    "used": "good",
    "usato": "good",
    "like_new": "mint",
    "come nuovo": "mint",
    "good": "good",
    "buono": "good",
    "fair": "fair",
    "discreto": "fair",
    "refurbished": "fair",
    "ricondizionato": "fair",
}

_HEADERS_HTML = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.3",
    "DNT": "1",
}

_HEADERS_API = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://www.subito.it/",
    "X-Subito-Environment-ID": "",
}


# ---------------------------------------------------------------------------
# Price parsing helpers
# ---------------------------------------------------------------------------

def _parse_price(raw) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        p = float(raw)
        return p if p > 100 else None
    if isinstance(raw, dict):
        amount = raw.get("amount") or raw.get("value") or raw.get("price")
        if amount:
            return _parse_price(amount)
        fv = raw.get("formatted_value") or raw.get("formatted") or ""
        return _parse_price_text(str(fv))
    return _parse_price_text(str(raw))


def _parse_price_text(text: str) -> float | None:
    if not text:
        return None
    low = text.lower()
    if any(w in low for w in ["trattabil", "trattare", "contatt", "gratis", "free"]):
        return None
    text = text.replace(" ", "").replace("\xa0", "").replace(" ", "")
    m = re.search(r"([\d\.]+(?:,\d{1,2})?)\s*€", text)
    if not m:
        m = re.search(r"€\s*([\d\.]+(?:,\d{1,2})?)", text)
    if not m:
        return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        p = float(raw)
        return p if p > 100 else None
    except ValueError:
        return None


def _extract_price_from_ad(ad: dict) -> float | None:
    """Estrae prezzo dalla struttura Hades API."""
    features = ad.get("features") or []
    for f in features:
        if f.get("uri") == "/price":
            vals = f.get("values") or []
            if vals:
                key = vals[0].get("key") or ""
                label = vals[0].get("value") or vals[0].get("label") or ""
                p = _parse_price(key) or _parse_price_text(label)
                if p:
                    return p
    return _parse_price(ad.get("price") or ad.get("prices", {}).get("price", {}))


# ---------------------------------------------------------------------------
# Condition extraction
# ---------------------------------------------------------------------------

def _extract_condition(ad: dict) -> str:
    """
    Estrae condizione dell'annuncio.
    Hades espone la condizione come feature /item_condition o nel tipo annuncio.
    """
    features = ad.get("features") or []
    for f in features:
        uri = f.get("uri", "")
        if "condition" in uri or "state" in uri:
            vals = f.get("values") or []
            if vals:
                raw_key = str(vals[0].get("key", "")).lower()
                raw_val = str(vals[0].get("value", "") or vals[0].get("label", "")).lower()
                # Prova prima la chiave, poi il valore testuale
                for candidate in (raw_key, raw_val):
                    mapped = _CONDITION_MAP.get(candidate)
                    if mapped:
                        return mapped
                # Ricerca parziale
                for trigger, result in _CONDITION_MAP.items():
                    if trigger in raw_key or trigger in raw_val:
                        return result

    # Fallback: campo type dell'annuncio
    ad_type = str(ad.get("type", {}).get("key", "") if isinstance(ad.get("type"), dict) else ad.get("type", "")).lower()
    for trigger, result in _CONDITION_MAP.items():
        if trigger in ad_type:
            return result

    return "unknown"


# ---------------------------------------------------------------------------
# Relevance check
# ---------------------------------------------------------------------------

def _is_relevant_to_query(title: str, reference: str) -> bool:
    """
    Controlla che il titolo contenga almeno un token significativo
    della referenza cercata. Necessario perché Subito con qso=false
    cerca in tutto il testo e può restituire orologi sbagliati.
    """
    title_up = title.upper()
    ref_up = reference.upper()
    tokens = [t for t in re.split(r"[\s/\-]+", ref_up) if len(t) >= 3]
    return any(token in title_up for token in tokens)


# ---------------------------------------------------------------------------
# Main scraper
# ---------------------------------------------------------------------------

async def scrape(reference: str, context=None) -> list[WatchListing]:
    """
    Scrapa Subito.it con paginazione (fino a _MAX_PAGES pagine).

    Usa la categoria orologi da polso (cat=28) per ridurre il rumore.
    Estrae condizione, location e venditore da ogni annuncio.

    Args:
        reference: Referenza orologio, es. "116610LN" o "Rolex Submariner"
        context: BrowserContext Playwright (non usato, Subito usa API HTTP)

    Returns:
        Lista ordinata per prezzo di WatchListing validi.
    """
    listings: list[WatchListing] = []
    seen_urls: set[str] = set()

    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            http2=False,
        ) as client:
            # Step 1: priming cookies con la pagina categoria orologi
            try:
                await client.get(
                    _PRIME_URL,
                    params={"q": reference},
                    headers=_HEADERS_HTML,
                )
                logger.debug("Subito: cookie priming completato")
            except Exception:
                pass  # continua anche senza cookies

            # Step 2: pagine multiple
            for page_idx in range(_MAX_PAGES):
                start_offset = page_idx * _PAGE_SIZE

                params = {
                    "q": reference,
                    "t": "s",               # for sale
                    "sort": "datedesc",
                    "lim": str(_PAGE_SIZE),
                    "start": str(start_offset),
                    "qso": "false",         # cerca in tutto il testo
                    "cat": "28",            # Orologi da polso
                }

                logger.info(
                    f"Subito: Hades API pagina {page_idx + 1}/{_MAX_PAGES} "
                    f"(start={start_offset}) per '{reference}'"
                )

                try:
                    r = await client.get(
                        _HADES_URL,
                        params=params,
                        headers=_HEADERS_API,
                    )
                except Exception as e:
                    logger.error(f"Subito: errore HTTP pagina {page_idx + 1}: {e}")
                    break

                if r.status_code != 200:
                    logger.warning(
                        f"Subito Hades status {r.status_code} alla pagina {page_idx + 1}"
                    )
                    break

                try:
                    data = r.json()
                except Exception:
                    logger.warning("Subito: risposta non è JSON valido")
                    break

                ads = data.get("ads") or []
                logger.info(
                    f"Subito: {len(ads)} annunci (pagina {page_idx + 1}) per '{reference}'"
                )

                # Se la pagina è vuota, non ha senso continuare
                if not ads:
                    break

                for ad in ads:
                    try:
                        title = ad.get("subject") or ad.get("title") or ""
                        if not title:
                            continue

                        price = _extract_price_from_ad(ad)
                        if not price or price < 1500:
                            continue

                        urls = ad.get("urls") or {}
                        url = (
                            urls.get("default")
                            or urls.get("www")
                            or ad.get("url")
                            or ""
                        )
                        if not url:
                            continue
                        if not url.startswith("http"):
                            url = "https://www.subito.it" + url

                        if url in seen_urls:
                            continue
                        seen_urls.add(url)

                        # Filtra accessori
                        if not is_watch_listing(title, "", price):
                            continue

                        # Filtra irrilevanti per la query
                        if not _is_relevant_to_query(title, reference):
                            logger.debug(
                                f"Subito: skip irrilevante '{title[:50]}' per '{reference}'"
                            )
                            continue

                        geo = ad.get("geo") or {}
                        city = (
                            geo.get("city", {}).get("value")
                            or geo.get("region", {}).get("value")
                            or "Italia"
                        )

                        advertiser = ad.get("advertiser") or {}
                        is_company = (
                            advertiser.get("company", False)
                            or advertiser.get("type", 0) == 2
                        )
                        seller = (
                            advertiser.get("name")
                            or advertiser.get("company_name")
                            or ("Negozio Subito" if is_company else "Privato")
                        )
                        source = "reseller_website" if is_company else "subito"

                        condition = _extract_condition(ad)

                        listings.append(
                            WatchListing(
                                source=source,
                                reference=reference,
                                price=price,
                                currency="EUR",
                                seller=seller,
                                url=url,
                                condition=condition,
                                scraped_at=datetime.now(),
                                location=city,
                                description=title,
                            )
                        )

                    except Exception as e:
                        logger.debug(f"Subito ad parse error: {e}")
                        continue

    except Exception as e:
        logger.error(f"Subito error: {e}")

    listings.sort(key=lambda x: x.price)
    logger.info(f"Subito: {len(listings)} listing validi per '{reference}'")
    return listings
