"""
Antiquorum scraper.
Sito: https://www.antiquorum.swiss

Strategia a 2 livelli:
  1. httpx + BeautifulSoup sulle pagine di risultati (sito semplice, non Cloudflare-protetto)
  2. Playwright fallback se httpx viene bloccato

Antiquorum è basato a Ginevra ed è più accessibile rispetto ad aggregatori
come Invaluable/LiveAuctioneers da IP datacenter.
"""
import asyncio
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.antiquorum.swiss"

# URL da testare per i risultati — Antiquorum ha cambiato struttura nel tempo
RESULTS_URLS = [
    f"{BASE_URL}/en/auction-results",
    f"{BASE_URL}/en/results",
    f"{BASE_URL}/en/lots/results",
    f"{BASE_URL}/lots/results",
    f"{BASE_URL}/auction-results",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": BASE_URL,
}

FX_TO_CHF = {
    "CHF": 1.0,
    "USD": 0.88,
    "EUR": 0.95,
    "GBP": 1.12,
    "HKD": 0.113,
}

KNOWN_BRANDS = [
    "Rolex", "Patek Philippe", "Audemars Piguet", "F.P. Journe",
    "Richard Mille", "Omega", "Cartier", "Vacheron Constantin",
    "A. Lange & Söhne", "Breguet", "IWC", "Jaeger-LeCoultre",
    "Girard-Perregaux", "Ulysse Nardin", "Blancpain", "Tudor",
    "Longines", "Zenith", "TAG Heuer", "Hublot", "Panerai",
    "Chopard", "Piguet", "Le Coultre",
]


def _detect_brand(text: str) -> str | None:
    for brand in KNOWN_BRANDS:
        if brand.lower() in text.lower():
            return brand
    return None


def _parse_price_string(text: str) -> float | None:
    """Parsa 'CHF 432,500' o 'CHF 1.234.567' o 'USD 180,000'."""
    if not text or text.strip() in ("", "N/A", "-", "Estimate on Request"):
        return None

    # Trova valuta
    currency = "CHF"
    for cur in FX_TO_CHF:
        if cur in text.upper():
            currency = cur
            break

    # Rimuovi separatori ambigui: punto e virgola
    clean = text.replace(",", "").replace(".", "")
    nums = re.findall(r"\d+", clean)
    if not nums:
        return None
    try:
        amount = float(nums[0])
        if amount < 100:
            return None
        return round(amount * FX_TO_CHF.get(currency, 1.0), 0)
    except ValueError:
        return None


def _parse_estimate_str(text: str) -> tuple[float | None, float | None]:
    """Parsa 'CHF 150,000 - 300,000'."""
    if not text or "request" in text.lower():
        return None, None
    nums = re.findall(r"[\d,]+", text)
    nums_clean = []
    for n in nums:
        try:
            nums_clean.append(float(n.replace(",", "")))
        except ValueError:
            pass
    if len(nums_clean) >= 2:
        return nums_clean[0], nums_clean[1]
    elif len(nums_clean) == 1:
        return nums_clean[0], nums_clean[0]
    return None, None


def _parse_lot_card(card, base_url: str = BASE_URL) -> dict | None:
    """Parsa una card/tile di un singolo lotto dalla pagina listing."""
    result: dict[str, Any] = {
        "auction_house": "Antiquorum",
        "currency": "CHF",
        "buyer_premium_pct": 26.0,
        "sale_date": "2024-01-01",
    }

    # URL del lotto
    link = card.find("a", href=True)
    if link:
        href = link["href"]
        result["lot_url"] = href if href.startswith("http") else f"{base_url}{href}"

    # Titolo / descrizione
    title = ""
    for sel in [
        card.find(class_=re.compile(r"lot.?title|item.?title|watch.?name|product.?name", re.I)),
        card.find("h2"),
        card.find("h3"),
        card.find("h4"),
    ]:
        if sel:
            title = sel.get_text(strip=True)
            break

    if not title and link:
        title = link.get_text(strip=True)

    if not title:
        return None

    result["description"] = title
    brand = _detect_brand(title)
    result["brand"] = brand or "Unknown"
    result["model"] = title.replace(brand, "").strip(" ,.-") if brand else title

    # Numero lotto
    lot_el = card.find(class_=re.compile(r"lot.?num|lot.?number", re.I))
    if not lot_el:
        lot_el = card.find(string=re.compile(r"lot\s*[:#]?\s*\d+", re.I))
    if lot_el:
        m = re.search(r"(\d+)", str(lot_el))
        if m:
            result["lot_number"] = m.group(1)

    # Prezzo realizzato
    price_el = card.find(class_=re.compile(
        r"hammer|sold|price.?realiz|result|winning|realized", re.I
    ))
    if price_el:
        val = _parse_price_string(price_el.get_text())
        if val and val > 500:
            result["hammer_price_chf"] = val
            result["total_price_chf"] = round(val * 1.26)

    # Stima
    est_el = card.find(class_=re.compile(r"estimate|stima|estimation", re.I))
    if est_el:
        low, high = _parse_estimate_str(est_el.get_text())
        result["estimate_low_chf"] = low
        result["estimate_high_chf"] = high

    # Data asta
    date_el = card.find(class_=re.compile(r"date|sale.?date|auction.?date", re.I))
    if date_el:
        date_text = date_el.get_text(strip=True)
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_text)
        if m:
            result["sale_date"] = m.group(0)
        else:
            # Prova formato "DD Month YYYY"
            months = {
                "january": "01", "february": "02", "march": "03", "april": "04",
                "may": "05", "june": "06", "july": "07", "august": "08",
                "september": "09", "october": "10", "november": "11", "december": "12",
            }
            m2 = re.search(
                r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", date_text
            )
            if m2:
                day, mon, year = m2.groups()
                mon_num = months.get(mon.lower(), "01")
                result["sale_date"] = f"{year}-{mon_num}-{day.zfill(2)}"

    # Immagine
    img = card.find("img")
    if img:
        src = img.get("src") or img.get("data-src") or ""
        if src:
            result["image_url"] = src if src.startswith("http") else f"{base_url}{src}"

    # Sale name dal contesto
    sale_el = card.find(class_=re.compile(r"sale.?name|auction.?name|sale.?title", re.I))
    if sale_el:
        result["sale_name"] = sale_el.get_text(strip=True)

    return result


def _parse_lot_detail_page(html: str, url: str) -> dict:
    """Parsa la pagina HTML di un singolo lotto Antiquorum (pagina dettaglio)."""
    soup = BeautifulSoup(html, "html.parser")
    result: dict[str, Any] = {
        "auction_house": "Antiquorum",
        "lot_url": url,
        "currency": "CHF",
        "buyer_premium_pct": 26.0,
        "sale_date": "2024-01-01",
    }

    # Titolo principale
    title_el = (
        soup.find("h1")
        or soup.find(class_=re.compile(r"lot.?title|item.?title", re.I))
    )
    title = title_el.get_text(strip=True) if title_el else ""
    result["description"] = title

    brand = _detect_brand(title)
    result["brand"] = brand or "Unknown"
    result["model"] = title.replace(brand, "").strip(" ,.-") if brand else title

    # Lot number
    lot_el = soup.find(string=re.compile(r"lot\s*[:#]?\s*\d+", re.I))
    if lot_el:
        m = re.search(r"(\d+)", str(lot_el))
        if m:
            result["lot_number"] = m.group(1)

    # Dati strutturati in tabella o lista definizioni
    details = {}
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) == 2:
            key = cells[0].get_text(strip=True).lower()
            val = cells[1].get_text(strip=True)
            details[key] = val

    for dl in soup.find_all("dl"):
        terms = dl.find_all("dt")
        defs = dl.find_all("dd")
        for t, d in zip(terms, defs):
            details[t.get_text(strip=True).lower()] = d.get_text(strip=True)

    # Referenza
    for k in ("reference", "ref.", "ref", "referenz", "réf."):
        if k in details:
            result["reference"] = details[k]
            break

    # Anno
    for k in ("year", "anno", "year made", "circa", "year of manufacture"):
        if k in details:
            result["year_made"] = details[k]
            break

    # Stima
    for k in ("estimate", "stima", "estimation", "estimate price"):
        if k in details:
            low, high = _parse_estimate_str(details[k])
            result["estimate_low_chf"] = low
            result["estimate_high_chf"] = high
            break

    # Hammer price
    for k in ("hammer price", "sold for", "price realized", "prezzo", "sold", "realised", "realized"):
        if k in details:
            result["hammer_price_chf"] = _parse_price_string(details[k])
            if result["hammer_price_chf"]:
                result["total_price_chf"] = round(result["hammer_price_chf"] * 1.26)
            break

    # Fallback: cerca prezzi in elementi con classi specifiche
    if not result.get("hammer_price_chf"):
        for el in soup.find_all(class_=re.compile(
            r"hammer|sold|price.realized|result|winning|realised", re.I
        )):
            val = _parse_price_string(el.get_text())
            if val and val > 500:
                result["hammer_price_chf"] = val
                result["total_price_chf"] = round(val * 1.26)
                break

    # Data asta
    date_el = soup.find(class_=re.compile(r"sale.?date|auction.?date", re.I))
    if date_el:
        date_text = date_el.get_text(strip=True)
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_text)
        if m:
            result["sale_date"] = m.group(0)

    # Sale name
    sale_el = soup.find(class_=re.compile(r"sale.?name|sale.?title|auction.?name", re.I))
    if sale_el:
        result["sale_name"] = sale_el.get_text(strip=True)

    # Immagine
    img = soup.find("img", class_=re.compile(r"lot.?image|main.?image|watch", re.I))
    if not img:
        img = soup.find("img", src=re.compile(r"lot|watch|image", re.I))
    if img and img.get("src"):
        src = img["src"]
        result["image_url"] = src if src.startswith("http") else f"{BASE_URL}{src}"

    return result


async def _try_fetch_listing(client: httpx.AsyncClient) -> tuple[str | None, str | None]:
    """Tenta il fetch della pagina listing su più URL candidati. Ritorna (html, url)."""
    for url in RESULTS_URLS:
        try:
            resp = await client.get(url)
            if resp.status_code == 200 and len(resp.text) > 2000:
                logger.info(f"Antiquorum: pagina risultati trovata su {url}")
                return resp.text, url
        except Exception as e:
            logger.debug(f"Antiquorum: {url} → {e}")
    return None, None


async def _playwright_fetch() -> list[dict]:
    """Fallback Playwright: naviga il sito e cattura i dati."""
    from playwright.async_api import async_playwright

    results = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            context = await browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 900},
            )
            page = await context.new_page()

            # Tenta tutti gli URL candidati
            html = None
            for url in RESULTS_URLS:
                try:
                    await page.goto(url, wait_until="networkidle", timeout=20000)
                    content = await page.content()
                    if len(content) > 3000:
                        html = content
                        logger.info(f"Antiquorum Playwright: pagina caricata da {url}")
                        break
                except Exception as e:
                    logger.debug(f"Antiquorum Playwright {url}: {e}")

            if html:
                soup = BeautifulSoup(html, "html.parser")
                # Cerca container di lotti
                for container_class in [
                    re.compile(r"lot.?card|lot.?item|lot.?tile|result.?item|auction.?item", re.I),
                    re.compile(r"grid.?item|product.?card|watch.?card", re.I),
                ]:
                    cards = soup.find_all(class_=container_class)
                    if cards:
                        logger.info(f"Antiquorum Playwright: {len(cards)} card trovate")
                        for card in cards[:50]:
                            parsed = _parse_lot_card(card)
                            if parsed and parsed.get("brand") != "Unknown":
                                results.append(parsed)
                        break

            await context.close()
            await browser.close()

    except Exception as e:
        logger.error(f"Antiquorum Playwright: {e}")

    return results


async def scrape_recent_results(limit: int = 50) -> list[dict]:
    """Scarica i risultati più recenti da Antiquorum."""
    logger.info(f"Antiquorum scraper: fetch risultati (limit={limit})")
    results = []

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        html, found_url = await _try_fetch_listing(client)

        if html:
            soup = BeautifulSoup(html, "html.parser")

            # Strategia 1: cerca card di lotti
            lot_cards = []
            for container_class in [
                re.compile(r"lot.?card|lot.?item|lot.?tile|result.?item|auction.?item", re.I),
                re.compile(r"grid.?item|product.?card|watch.?card|item.?card", re.I),
                re.compile(r"lot$|item$|result$", re.I),
            ]:
                cards = soup.find_all(class_=container_class)
                if cards:
                    logger.info(f"Antiquorum: {len(cards)} card trovate con selector")
                    lot_cards = cards
                    break

            if lot_cards:
                for card in lot_cards[:limit]:
                    parsed = _parse_lot_card(card, BASE_URL)
                    if parsed and parsed.get("brand") != "Unknown":
                        results.append(parsed)

            # Strategia 2: se non troviamo card, cerca link diretti ai lotti
            if not results:
                lot_links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    # Antiquorum usa URL come /en/lot/12345 o /lots/12345
                    if re.search(r"/lot[s]?/\d+|/auction.*/\d+", href, re.I):
                        full = href if href.startswith("http") else f"{BASE_URL}{href}"
                        if full not in lot_links:
                            lot_links.append(full)
                        if len(lot_links) >= limit:
                            break

                logger.info(f"Antiquorum: {len(lot_links)} link lotti trovati")

                for url in lot_links[:limit]:
                    try:
                        r = await client.get(url)
                        r.raise_for_status()
                        lot_data = _parse_lot_detail_page(r.text, url)
                        if lot_data.get("brand") and lot_data["brand"] != "Unknown":
                            results.append(lot_data)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.debug(f"Antiquorum errore lotto {url}: {e}")

    # Fallback Playwright se httpx non ha prodotto risultati
    if not results:
        logger.info("Antiquorum: fallback Playwright")
        results = await _playwright_fetch()

    logger.info(f"Antiquorum: estratti {len(results)} risultati")
    return results[:limit]


async def scrape_reference(reference: str) -> list[dict]:
    """Cerca su Antiquorum i risultati per una referenza specifica."""
    logger.info(f"Antiquorum scraper: ricerca '{reference}'")
    results = []

    search_urls = [
        f"{BASE_URL}/en/search",
        f"{BASE_URL}/search",
        f"{BASE_URL}/en/lots",
    ]

    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0, follow_redirects=True) as client:
        for search_url in search_urls:
            try:
                resp = await client.get(search_url, params={"q": reference, "type": "lot"})
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                # Cerca link lotti nella pagina risultati
                lot_links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if re.search(r"/lot[s]?/\d+|/auction.*/\d+", href, re.I):
                        full = href if href.startswith("http") else f"{BASE_URL}{href}"
                        if full not in lot_links:
                            lot_links.append(full)

                if lot_links:
                    for url in lot_links[:20]:
                        try:
                            r = await client.get(url)
                            lot_data = _parse_lot_detail_page(r.text, url)
                            lot_data["reference"] = reference
                            results.append(lot_data)
                            await asyncio.sleep(0.4)
                        except Exception as e:
                            logger.debug(f"Antiquorum ricerca errore {url}: {e}")
                    break

            except Exception as e:
                logger.error(f"Antiquorum scraper ricerca '{reference}' su {search_url}: {e}")

    return results
