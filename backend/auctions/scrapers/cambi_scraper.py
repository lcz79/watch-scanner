"""
Cambi Casa d'Aste scraper.
Casa d'aste italiana con sede a Genova.
Sito: https://www.cambiaste.com

Cambi tiene aste di orologi periodicamente come parte delle loro vendite
di "Gioielli, Orologi e Oggetti Preziosi".
"""
import asyncio
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.cambiaste.com"

RESULTS_URLS = [
    f"{BASE_URL}/it/risultati/",
    f"{BASE_URL}/it/archivio/",
    f"{BASE_URL}/it/aste/",
    f"{BASE_URL}/it/lotti/",
    f"{BASE_URL}",
]

SEARCH_URL = f"{BASE_URL}/it/ricerca/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.5",
    "Referer": BASE_URL,
}

FX_TO_CHF = {"CHF": 1.0, "EUR": 0.95, "USD": 0.88, "GBP": 1.12}

KNOWN_BRANDS = [
    "Rolex", "Patek Philippe", "Audemars Piguet", "F.P. Journe",
    "Richard Mille", "Omega", "Cartier", "Vacheron Constantin",
    "A. Lange & Söhne", "Breguet", "IWC", "Jaeger-LeCoultre",
    "Girard-Perregaux", "Blancpain", "Tudor", "Longines", "Zenith",
    "TAG Heuer", "Hublot", "Panerai", "Chopard", "Baume & Mercier",
]


def _detect_brand(text: str) -> str | None:
    for brand in KNOWN_BRANDS:
        if brand.lower() in text.lower():
            return brand
    return None


def _parse_price(text: str) -> float | None:
    if not text or text.strip() in ("", "—", "-", "N/D", "n.v."):
        return None
    currency = "EUR"
    for cur in FX_TO_CHF:
        if cur in text.upper():
            currency = cur
            break
    nums = re.findall(r"\d+", text.replace(".", "").replace(",", "").replace(" ", ""))
    if not nums:
        return None
    try:
        amount = float(nums[0])
        if amount < 100:
            return None
        return round(amount * FX_TO_CHF.get(currency, 0.95), 0)
    except ValueError:
        return None


def _parse_card(card, base_url: str = BASE_URL) -> dict | None:
    result: dict[str, Any] = {
        "auction_house": "Cambi",
        "currency": "CHF",
        "buyer_premium_pct": 27.0,
        "sale_date": "2024-01-01",
        "sale_location": "Genova",
    }

    link = card.find("a", href=True)
    if link:
        href = link["href"]
        result["lot_url"] = href if href.startswith("http") else f"{base_url}{href}"

    title = ""
    for sel in [
        card.find(class_=re.compile(r"lot.?title|item.?title|lotto.?titolo|titolo", re.I)),
        card.find("h2"), card.find("h3"), card.find("h4"),
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

    # Prezzo realizzato
    for cls in [
        re.compile(r"prezzo.?realizz|hammer|aggiudicaz|prezzo.?final|venduto", re.I)
    ]:
        el = card.find(class_=cls)
        if el:
            val = _parse_price(el.get_text())
            if val:
                result["hammer_price_chf"] = val
                result["total_price_chf"] = round(val * 1.27)
                break

    # Stima
    est_el = card.find(class_=re.compile(r"stima|estimate|valutazione", re.I))
    if est_el:
        nums = re.findall(r"\d+", est_el.get_text().replace(".", "").replace(",", ""))
        if len(nums) >= 2:
            result["estimate_low_chf"] = float(nums[0]) * 0.95
            result["estimate_high_chf"] = float(nums[1]) * 0.95

    # Data
    date_el = card.find(class_=re.compile(r"data|date|sale.?date", re.I))
    if date_el:
        text_date = date_el.get_text(strip=True)
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text_date)
        if m:
            result["sale_date"] = m.group(0)
        else:
            months_it = {
                "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
                "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
                "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12",
            }
            m2 = re.search(r"(\d{1,2})\s+([a-zA-ZÀ-ÿ]+)\s+(\d{4})", text_date, re.IGNORECASE)
            if m2:
                day, mon, year = m2.groups()
                mon_num = months_it.get(mon.lower(), "01")
                result["sale_date"] = f"{year}-{mon_num}-{day.zfill(2)}"

    img = card.find("img")
    if img:
        src = img.get("src") or img.get("data-src") or ""
        if src:
            result["image_url"] = src if src.startswith("http") else f"{base_url}{src}"

    sale_el = card.find(class_=re.compile(r"asta.?nome|sale.?name|vendita", re.I))
    if sale_el:
        result["sale_name"] = sale_el.get_text(strip=True)

    return result


async def scrape_recent_results(limit: int = 40) -> list[dict]:
    """Scarica i risultati più recenti da Cambi."""
    logger.info(f"Cambi scraper: fetch risultati (limit={limit})")
    results = []

    async with httpx.AsyncClient(
        headers=HEADERS, timeout=30.0, follow_redirects=True
    ) as client:
        html = None
        found_url = None
        for url in RESULTS_URLS:
            try:
                resp = await client.get(url)
                if resp.status_code == 200 and len(resp.text) > 2000:
                    html = resp.text
                    found_url = url
                    logger.info(f"Cambi: pagina trovata su {url}")
                    break
            except Exception as e:
                logger.debug(f"Cambi: {url} → {e}")

        if not html:
            # Prova la homepage e cerca link alle aste
            try:
                resp = await client.get(BASE_URL)
                if resp.status_code == 200:
                    html = resp.text
                    found_url = BASE_URL
            except Exception as e:
                logger.error(f"Cambi: homepage non raggiungibile: {e}")

        if html:
            soup = BeautifulSoup(html, "html.parser")

            # Cerca card di lotti
            lot_cards = []
            for cls in [
                re.compile(r"lot.?card|lot.?item|lotto.?card|item.?lot", re.I),
                re.compile(r"card.?lotto|card.?lot|auction.?item|result.?item", re.I),
            ]:
                cards = soup.find_all(class_=cls)
                if cards:
                    lot_cards = cards
                    logger.info(f"Cambi: {len(cards)} card trovate")
                    break

            if lot_cards:
                for card in lot_cards[:limit]:
                    parsed = _parse_card(card, BASE_URL)
                    if parsed and parsed.get("brand") != "Unknown":
                        results.append(parsed)
            else:
                # Cerca link a lotti con pattern Cambi
                lot_links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if re.search(r"/lotto/|/lot/|/asta/.*\d+|/lotti/", href, re.I):
                        full = href if href.startswith("http") else f"{BASE_URL}{href}"
                        if full not in lot_links:
                            lot_links.append(full)
                        if len(lot_links) >= limit:
                            break

                logger.info(f"Cambi: {len(lot_links)} link lotti trovati")
                for url in lot_links[:limit]:
                    try:
                        r = await client.get(url)
                        if r.status_code == 200:
                            soup_lot = BeautifulSoup(r.text, "html.parser")
                            # Estrai dati dalla pagina lotto
                            parsed = _parse_detail_page(soup_lot, url)
                            if parsed and parsed.get("brand") != "Unknown":
                                results.append(parsed)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.debug(f"Cambi lotto {url}: {e}")

    if not results:
        logger.info("Cambi: nessun risultato con httpx, provo Playwright")
        results = await _playwright_fetch(limit)

    logger.info(f"Cambi: estratti {len(results)} risultati")
    return results[:limit]


def _parse_detail_page(soup: BeautifulSoup, url: str) -> dict | None:
    """Parsa una pagina lotto Cambi."""
    result: dict[str, Any] = {
        "auction_house": "Cambi",
        "lot_url": url,
        "currency": "CHF",
        "buyer_premium_pct": 27.0,
        "sale_date": "2024-01-01",
        "sale_location": "Genova",
    }

    title_el = soup.find("h1") or soup.find(class_=re.compile(r"lot.?title|titolo", re.I))
    title = title_el.get_text(strip=True) if title_el else ""
    if not title:
        return None

    result["description"] = title
    brand = _detect_brand(title)
    result["brand"] = brand or "Unknown"
    result["model"] = title.replace(brand, "").strip(" ,.-") if brand else title

    # Prezzo in tabella dettagli
    details = {}
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) == 2:
            details[cells[0].get_text(strip=True).lower()] = cells[1].get_text(strip=True)

    for k in ("prezzo realizzato", "aggiudicazione", "venduto per", "hammer", "prezzo finale"):
        if k in details:
            val = _parse_price(details[k])
            if val:
                result["hammer_price_chf"] = val
                result["total_price_chf"] = round(val * 1.27)
            break

    for k in ("stima", "valutazione", "estimate"):
        if k in details:
            nums = re.findall(r"\d+", details[k].replace(".", "").replace(",", ""))
            if len(nums) >= 2:
                result["estimate_low_chf"] = float(nums[0]) * 0.95
                result["estimate_high_chf"] = float(nums[1]) * 0.95
            break

    return result


async def _playwright_fetch(limit: int = 40) -> list[dict]:
    """Fallback Playwright per Cambi."""
    from playwright.async_api import async_playwright
    results = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = await browser.new_context(user_agent=HEADERS["User-Agent"], viewport={"width": 1280, "height": 900})
            page = await context.new_page()
            for url in RESULTS_URLS:
                try:
                    await page.goto(url, wait_until="networkidle", timeout=20000)
                    content = await page.content()
                    if len(content) > 3000:
                        soup = BeautifulSoup(content, "html.parser")
                        for cls in [re.compile(r"lot.?card|lotto.?card|item.?lot|result.?item", re.I)]:
                            cards = soup.find_all(class_=cls)
                            if cards:
                                for card in cards[:limit]:
                                    parsed = _parse_card(card, BASE_URL)
                                    if parsed and parsed.get("brand") != "Unknown":
                                        results.append(parsed)
                                break
                        if results:
                            break
                except Exception as e:
                    logger.debug(f"Cambi Playwright {url}: {e}")
            await context.close()
            await browser.close()
    except Exception as e:
        logger.error(f"Cambi Playwright: {e}")
    return results
