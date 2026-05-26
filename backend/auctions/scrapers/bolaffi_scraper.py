"""
Bolaffi Aste scraper.
Casa d'aste italiana con sede a Torino.
Sito: https://www.bolaffi.it

Bolaffi tiene aste periodiche di gioielli e orologi, spesso con ottime
opportunità su orologi vintage e sportivi italiani.
"""
import asyncio
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("auctions")

BASE_URL = "https://www.bolaffi.it"

RESULTS_URLS = [
    f"{BASE_URL}/aste/orologi/",
    f"{BASE_URL}/risultati/orologi/",
    f"{BASE_URL}/aste/risultati/",
    f"{BASE_URL}/catalogo/orologi/",
    f"{BASE_URL}/orologi/",
]

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
    "TAG Heuer", "Hublot", "Panerai", "Chopard", "Universal Genève",
    "Movado", "Heuer", "Tissot",
]


def _detect_brand(text: str) -> str | None:
    for brand in KNOWN_BRANDS:
        if brand.lower() in text.lower():
            return brand
    return None


def _parse_price(text: str, default_currency: str = "EUR") -> float | None:
    if not text or text.strip() in ("", "—", "-", "N/D", "n.v.", "Ritirato"):
        return None
    currency = default_currency
    for cur in FX_TO_CHF:
        if cur in text.upper():
            currency = cur
            break
    # Normalizza: rimuovi separatori di migliaia
    clean = re.sub(r"[^\d]", "", text.replace(".", "").replace(",", ""))
    if not clean:
        return None
    try:
        amount = float(clean)
        if amount < 100:
            return None
        return round(amount * FX_TO_CHF.get(currency, 0.95), 0)
    except ValueError:
        return None


def _parse_card(card, base_url: str = BASE_URL) -> dict | None:
    result: dict[str, Any] = {
        "auction_house": "Bolaffi",
        "currency": "CHF",
        "buyer_premium_pct": 25.0,
        "sale_date": "2024-01-01",
        "sale_location": "Torino",
    }

    link = card.find("a", href=True)
    if link:
        href = link["href"]
        result["lot_url"] = href if href.startswith("http") else f"{base_url}{href}"

    title = ""
    for sel in [
        card.find(class_=re.compile(r"lot.?title|titolo|nome|lotto", re.I)),
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

    # Prezzo
    for cls in [re.compile(r"prezzo|hammer|aggiudicaz|venduto|realizz", re.I)]:
        el = card.find(class_=cls)
        if el:
            val = _parse_price(el.get_text())
            if val:
                result["hammer_price_chf"] = val
                result["total_price_chf"] = round(val * 1.25)
                break

    # Stima
    est_el = card.find(class_=re.compile(r"stima|estimate|valut", re.I))
    if est_el:
        nums = re.findall(r"\d+", est_el.get_text().replace(".", "").replace(",", ""))
        if len(nums) >= 2:
            result["estimate_low_chf"] = float(nums[0]) * 0.95
            result["estimate_high_chf"] = float(nums[1]) * 0.95

    # Data
    date_el = card.find(class_=re.compile(r"data|date|sale", re.I))
    if date_el:
        dt = date_el.get_text(strip=True)
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", dt)
        if m:
            result["sale_date"] = m.group(0)
        else:
            months_it = {
                "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
                "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
                "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12",
            }
            m2 = re.search(r"(\d{1,2})\s+([a-zA-ZÀ-ÿ]+)\s+(\d{4})", dt, re.IGNORECASE)
            if m2:
                day, mon, year = m2.groups()
                mon_num = months_it.get(mon.lower(), "01")
                result["sale_date"] = f"{year}-{mon_num}-{day.zfill(2)}"

    img = card.find("img")
    if img:
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
        if src:
            result["image_url"] = src if src.startswith("http") else f"{base_url}{src}"

    return result


async def scrape_recent_results(limit: int = 40) -> list[dict]:
    """Scarica i risultati più recenti da Bolaffi."""
    logger.info(f"Bolaffi scraper: fetch risultati (limit={limit})")
    results = []

    async with httpx.AsyncClient(
        headers=HEADERS, timeout=30.0, follow_redirects=True
    ) as client:
        html = None
        for url in RESULTS_URLS:
            try:
                resp = await client.get(url)
                if resp.status_code == 200 and len(resp.text) > 2000:
                    html = resp.text
                    logger.info(f"Bolaffi: pagina trovata su {url}")
                    break
            except Exception as e:
                logger.debug(f"Bolaffi: {url} → {e}")

        if not html:
            try:
                resp = await client.get(BASE_URL)
                if resp.status_code == 200:
                    html = resp.text
            except Exception as e:
                logger.error(f"Bolaffi: homepage non raggiungibile: {e}")

        if html:
            soup = BeautifulSoup(html, "html.parser")

            lot_cards = []
            for cls in [
                re.compile(r"lot.?card|lotto.?card|item.?lot|watch.?item|orologio", re.I),
                re.compile(r"catalog.?item|product.?item|product.?card", re.I),
            ]:
                cards = soup.find_all(class_=cls)
                if cards:
                    lot_cards = cards
                    logger.info(f"Bolaffi: {len(cards)} card trovate")
                    break

            if lot_cards:
                for card in lot_cards[:limit]:
                    parsed = _parse_card(card, BASE_URL)
                    if parsed and parsed.get("brand") != "Unknown":
                        results.append(parsed)
            else:
                lot_links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if re.search(r"/lotto/\d+|/lot/\d+|/aste/.*\d{4,}|/orologi/.*\d+", href, re.I):
                        full = href if href.startswith("http") else f"{BASE_URL}{href}"
                        if full not in lot_links:
                            lot_links.append(full)
                        if len(lot_links) >= limit:
                            break

                logger.info(f"Bolaffi: {len(lot_links)} link lotti trovati")
                for url in lot_links[:limit]:
                    try:
                        r = await client.get(url)
                        if r.status_code == 200:
                            soup_lot = BeautifulSoup(r.text, "html.parser")
                            parsed = _parse_detail_page(soup_lot, url)
                            if parsed and parsed.get("brand") != "Unknown":
                                results.append(parsed)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.debug(f"Bolaffi lotto {url}: {e}")

    if not results:
        logger.info("Bolaffi: nessun risultato con httpx, provo Playwright")
        results = await _playwright_fetch(limit)

    logger.info(f"Bolaffi: estratti {len(results)} risultati")
    return results[:limit]


def _parse_detail_page(soup: BeautifulSoup, url: str) -> dict | None:
    """Parsa una pagina lotto Bolaffi."""
    result: dict[str, Any] = {
        "auction_house": "Bolaffi",
        "lot_url": url,
        "currency": "CHF",
        "buyer_premium_pct": 25.0,
        "sale_date": "2024-01-01",
        "sale_location": "Torino",
    }

    title_el = soup.find("h1") or soup.find(class_=re.compile(r"titolo|lot.?title|nome", re.I))
    title = title_el.get_text(strip=True) if title_el else ""
    if not title:
        return None

    result["description"] = title
    brand = _detect_brand(title)
    result["brand"] = brand or "Unknown"
    result["model"] = title.replace(brand, "").strip(" ,.-") if brand else title

    details = {}
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) == 2:
            details[cells[0].get_text(strip=True).lower()] = cells[1].get_text(strip=True)
    for dl in soup.find_all("dl"):
        for t, d in zip(dl.find_all("dt"), dl.find_all("dd")):
            details[t.get_text(strip=True).lower()] = d.get_text(strip=True)

    for k in ("prezzo realizzato", "aggiudicato", "venduto", "hammer", "risultato"):
        if k in details:
            val = _parse_price(details[k])
            if val:
                result["hammer_price_chf"] = val
                result["total_price_chf"] = round(val * 1.25)
            break

    for k in ("stima", "valutazione", "estimate", "stima di vendita"):
        if k in details:
            nums = re.findall(r"\d+", details[k].replace(".", "").replace(",", ""))
            if len(nums) >= 2:
                result["estimate_low_chf"] = float(nums[0]) * 0.95
                result["estimate_high_chf"] = float(nums[1]) * 0.95
            break

    for k in ("referenza", "ref.", "reference", "referenza orologio"):
        if k in details:
            result["reference"] = details[k]
            break

    return result


async def _playwright_fetch(limit: int = 40) -> list[dict]:
    """Fallback Playwright per Bolaffi."""
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
                        for cls in [re.compile(r"lot.?card|lotto.?card|catalog.?item|product.?card", re.I)]:
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
                    logger.debug(f"Bolaffi Playwright {url}: {e}")
            await context.close()
            await browser.close()
    except Exception as e:
        logger.error(f"Bolaffi Playwright: {e}")
    return results
