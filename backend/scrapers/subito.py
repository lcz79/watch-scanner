"""
Scraper per subito.it — usa l'API Hades interna (stessa usata dal sito).
Endpoint: https://www.subito.it/hades/v1/search/items
"""
import httpx
import re
from datetime import datetime
from models.schemas import WatchListing
from utils.logger import get_logger
from utils.watch_filter import is_watch_listing

logger = get_logger("scraper.subito")

_HADES_URL = "https://www.subito.it/hades/v1/search/items"

_PRIME_URL = "https://www.subito.it/annunci-italia/vendita/usato/"

_HEADERS_HTML = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.3",
    "DNT": "1",
}

_HEADERS_API = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://www.subito.it/",
    "X-Subito-Environment-ID": "",
}


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
    text = text.replace("\u202f", "").replace("\xa0", "").replace(" ", "")
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
    # Struttura Hades: features è una lista di {uri, label, values}
    features = ad.get("features") or []
    for f in features:
        if f.get("uri") == "/price":
            vals = f.get("values") or []
            if vals:
                # values[0] = {"key": "10500", "value": "10500 €"}
                key = vals[0].get("key") or ""
                label = vals[0].get("value") or vals[0].get("label") or ""
                p = _parse_price(key) or _parse_price_text(label)
                if p:
                    return p
    # Fallback: campo price diretto
    return _parse_price(ad.get("price") or ad.get("prices", {}).get("price", {}))


def _is_relevant_to_query(title: str, reference: str) -> bool:
    """
    Controlla che il titolo dell'annuncio sia effettivamente rilevante per la ricerca.
    Subito con qso=false cerca in tutto il testo → può restituire orologi sbagliati.
    Richiede che il titolo contenga almeno un token significativo della referenza.
    """
    title_up = title.upper()
    ref_up = reference.upper()
    tokens = [t for t in re.split(r'[\s/\-]+', ref_up) if len(t) >= 3]
    # Per referenze numeriche (es. 116610LN), basta che il numero sia nel titolo
    for token in tokens:
        if token in title_up:
            return True
    return False


async def scrape(reference: str, context=None) -> list[WatchListing]:
    listings = []
    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            http2=False,
        ) as client:
            # Step 1: prime cookies con pagina HTML
            try:
                await client.get(
                    _PRIME_URL,
                    params={"q": reference},
                    headers=_HEADERS_HTML,
                )
            except Exception:
                pass  # anche senza cookies, proviamo l'API

            # Step 2: chiama Hades API
            params = {
                "q": reference,
                "t": "s",           # for sale
                "sort": "datedesc",
                "lim": "40",
                "start": "0",
                "qso": "false",     # cerca in tutto il testo, non solo titolo
            }

            logger.info(f"Subito: Hades API search per {reference}")
            r = await client.get(_HADES_URL, params=params, headers=_HEADERS_API)

            if r.status_code != 200:
                logger.warning(f"Subito Hades status {r.status_code}")
                return []

            try:
                data = r.json()
            except Exception:
                logger.warning("Subito: risposta non è JSON valido")
                return []

            ads = data.get("ads") or []
            logger.info(f"Subito: {len(ads)} annunci dall'API per {reference}")

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

                    geo = ad.get("geo") or {}
                    city = (
                        geo.get("city", {}).get("value")
                        or geo.get("region", {}).get("value")
                        or "Italia"
                    )

                    advertiser = ad.get("advertiser") or {}
                    is_company = advertiser.get("company", False) or advertiser.get("type", 0) == 2
                    seller = advertiser.get("name") or advertiser.get("company_name") or (
                        "Negozio Subito" if is_company else "Privato"
                    )
                    source = "reseller_website" if is_company else "subito"

                    if not is_watch_listing(title, "", price):
                        continue

                    if not _is_relevant_to_query(title, reference):
                        logger.debug(f"Subito: skip irrilevante '{title[:50]}' per query '{reference}'")
                        continue

                    listings.append(WatchListing(
                        source=source,
                        reference=reference,
                        price=price,
                        currency="EUR",
                        seller=seller,
                        url=url,
                        condition="unknown",
                        scraped_at=datetime.now(),
                        location=city,
                        description=title,
                    ))

                except Exception as e:
                    logger.debug(f"Subito ad parse error: {e}")
                    continue

    except Exception as e:
        logger.error(f"Subito error: {e}")

    listings.sort(key=lambda x: x.price)
    logger.info(f"Subito: {len(listings)} listing validi per {reference}")
    return listings
