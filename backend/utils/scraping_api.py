"""
Scraping API helper — recupera l'HTML renderizzato di una pagina protetta da
Cloudflare instradando la richiesta tramite un servizio con proxy residenziali
(ScraperAPI o ZenRows). Usato per Chrono24, bloccato dagli IP datacenter.

Attivo solo se SCRAPER_API_KEY è configurata in backend/.env. Altrimenti gli
scraper continuano a usare Playwright diretto (comportamento invariato).
"""
import httpx

from config import get_settings
from utils.logger import get_logger

logger = get_logger("scraping_api")


def is_enabled() -> bool:
    return bool(get_settings().scraper_api_key)


def fetch_rendered_html(url: str, timeout: float = 50.0) -> str | None:
    """
    Ritorna l'HTML finale (post-Cloudflare, JS renderizzato) della pagina target,
    oppure None se la chiave non è configurata o la richiesta fallisce.
    """
    s = get_settings()
    key = s.scraper_api_key
    if not key:
        return None

    provider = (s.scraper_api_provider or "scraperapi").lower()
    country = s.scraper_api_country or "it"

    if provider == "zenrows":
        api_url = "https://api.zenrows.com/v1/"
        params = {
            "apikey": key,
            "url": url,
            "js_render": "true",
            "premium_proxy": "true",
            "proxy_country": country,
        }
    else:  # default: scraperapi
        api_url = "http://api.scraperapi.com/"
        params = {
            "api_key": key,
            "url": url,
            "render": "true",
            "premium": "true",
            "country_code": country,
        }

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            r = client.get(api_url, params=params)
            if r.status_code == 200 and len(r.text) > 1000:
                logger.info(f"Scraping API ({provider}): OK {len(r.text)}b per {url[:60]}")
                return r.text
            logger.warning(f"Scraping API ({provider}): status {r.status_code}, len {len(r.text)} per {url[:60]}")
    except Exception as e:
        logger.error(f"Scraping API ({provider}) errore: {e}")
    return None
