"""
ReferenceSpider: data una collection WatchBase, estrae tutte le referenze.

URL pattern:
  Collection: https://watchbase.com/{brand}/{collection}
  Reference:  https://watchbase.com/{brand}/{collection}/{ref-slug}

Ref slug format: {ref_code}-{variant_4digits}  es. 116500ln-0001
  → reference: 116500LN
  → variant: 0001
"""
import re, time, logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from config import BASE_URL
from fetcher import get_html

log = logging.getLogger("reference_spider")

_YEAR_RE     = re.compile(r"(19\d{2}|20\d{2})")
_VARIANT_SUF = re.compile(r"-(\d{4})$")   # suffisso variante: -0001, -0040, ecc.


def _ref_from_slug(slug: str) -> str:
    """
    Estrae codice referenza dallo slug WatchBase.
    '116500ln-0001' → '116500LN'
    '18038'         → '18038'
    '5711-1a-001'   → '5711/1A' (caso Patek con slash → da slug: 5711-1a)
    """
    # Rimuovi suffisso variante numerico finale
    clean = _VARIANT_SUF.sub("", slug)
    # Uppercase
    return clean.upper()


def _parse_years(text: str) -> tuple[int | None, int | None]:
    years = [int(y) for y in _YEAR_RE.findall(text)]
    if not years:
        return None, None
    y_from = min(years)
    y_to = max(years) if len(years) > 1 else None
    if any(w in text.lower() for w in ("present", "current", "oggi", "attuale")):
        y_to = None
    return y_from, y_to


def _fmt_year_range(y_from, y_to) -> str:
    if not y_from:
        return ""
    return f"{y_from}–present" if not y_to else f"{y_from}–{y_to}"


def _infer_tags(brand: str, model: str, movement: str) -> list[str]:
    tags: list[str] = []
    m, mv = model.lower(), movement.lower()
    if any(k in m for k in ("submariner", "diver", "aquanaut", "pelagos", "aquaracer")):
        tags.append("diving")
    if any(k in m for k in ("daytona", "chrono", "speedmaster", "carrera", "navitimer")):
        tags.append("chronograph")
    if any(k in m for k in ("gmt", "sky-dweller", "world time", "globemaster")):
        tags.append("gmt")
    if "perpetual" in m:
        tags.append("perpetual-calendar")
    if "date" in m and "datejust" not in m:
        tags.append("date")
    if any(k in m for k in ("explorer", "pilot", "flieger", "aviation")):
        tags.append("pilot")
    if "tourbillon" in mv or "tourbillon" in m:
        tags.append("tourbillon")
    if any(k in m for k in ("vintage", "heritage", "historique")):
        tags.append("vintage")
    if "royal oak" in m:
        tags.append("royal-oak")
    if "nautilus" in m:
        tags.append("nautilus")
    if not tags:
        tags.append(brand.lower().replace(" ", "-")[:20])
    return tags


_REF_CODE_CLEAN = re.compile(r"\(.*?\)|aka:.*", re.IGNORECASE)


def _scrape_ref_page(url: str, brand: str, model: str, ref_code: str) -> dict | None:
    """Scarica pagina singola referenza su WatchBase, estrae metadati dalla table."""
    html = get_html(url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")

    # WatchBase: table con <th> per label e <td> per valore (una per riga)
    specs: dict[str, str] = {}
    for row in soup.select("table tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            k = th.get_text(strip=True).lower().rstrip(":")
            v = td.get_text(strip=True)
            if k and v:
                specs[k] = v

    # Reference canonica dalla pagina (più affidabile dello slug)
    wb_ref = specs.get("reference", "")
    if wb_ref:
        # "116500LN-0001(aka: m116500ln-0001)" → "116500LN"
        wb_ref = _REF_CODE_CLEAN.sub("", wb_ref).strip()
        # Rimuovi suffisso variante -XXXX se numerico
        wb_ref = _VARIANT_SUF.sub("", wb_ref).strip()
        if wb_ref:
            ref_code = wb_ref.upper()

    # Nome/descrizione watch
    watch_name = specs.get("name", "")

    # Anno di produzione — WatchBase usa "Produced: 2016 - 2023"
    year_raw = specs.get("produced", specs.get("year", specs.get("introduced", "")))
    y_from, y_to = _parse_years(year_raw)

    # Movement: "Rolex caliber 4130Hours, Minutes, ..." → prendi solo la prima parte
    movement_full = specs.get("movement", "")
    # Estrai solo la parte del calibro (prima della virgola o dei dettagli)
    movement = re.split(r"Hours|Minutes|Seconds|,", movement_full)[0].strip() if movement_full else ""

    # Diametro cassa
    case_size = specs.get("diameter", specs.get("case diameter", specs.get("case size", "")))
    if case_size:
        # "40.00 mm" → "40mm"
        m = re.search(r"(\d+(?:\.\d+)?)\s*mm", case_size, re.IGNORECASE)
        case_size = f"{float(m.group(1)):.0f}mm" if m else case_size

    # Materiali
    materials = specs.get("materials", "")

    # Immagine: evita placeholder eBay/affiliati, prendi solo immagini watch reali
    img_url = ""
    _IMG_BLACKLIST = ("logo", "icon", "banner", "ad", "pixel", "1x1",
                      "referral", "ebay", "amazon", "affiliat", "sponsor",
                      "watermark", "placeholder", "noimage", "default")
    for img in soup.select("img[src]"):
        src = img.get("src", "")
        if not src:
            continue
        src_low = src.lower()
        if any(x in src_low for x in _IMG_BLACKLIST):
            continue
        if src.endswith((".jpg", ".jpeg", ".png", ".webp")):
            img_url = src if src.startswith("http") else f"https://watchbase.com{src}"
            break

    id_brand = re.sub(r"[^a-z0-9]+", "-", brand.lower()).strip("-")
    id_ref   = re.sub(r"[^a-z0-9]+", "-", ref_code.lower()).strip("-")

    return {
        "id": f"{id_brand}-{id_ref}",
        "brand": brand,
        "model": model,
        "reference": ref_code,
        "canonical_name": f"{brand} {model} {ref_code}",
        "year_range": _fmt_year_range(y_from, y_to),
        "movement": movement,
        "case_size": case_size,
        "image_url": img_url,
        "tags": _infer_tags(brand, model, movement),
        "avg_price_eur": 0,
        "_wb_url": url,
        "_wb_name": watch_name,
        "_materials": materials,
    }


def get_references(collection: dict, brand_name: str, max_refs: int = 200) -> list[dict]:
    """
    Legge la pagina di una collection WatchBase e scrapa ogni referenza.
    Gestisce paginazione WatchBase (page parameter: ?p=2, ?p=3 ...).
    """
    brand_slug = urlparse(collection["url"]).path.strip("/").split("/")[0]
    col_slug   = collection["slug"]

    results:     list[dict] = []
    seen_refs:   set[str]   = set()
    page        = 1
    max_pages   = 20  # safety cap

    while page <= max_pages and len(results) < max_refs:
        page_url = collection["url"] if page == 1 else f"{collection['url']}?p={page}"
        html = get_html(page_url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        new_on_page = 0

        for a in soup.select("a[href]"):
            href = a.get("href", "")
            parsed = urlparse(href)
            parts  = [p for p in parsed.path.strip("/").split("/") if p]

            # Vogliamo link della forma /brand/collection/ref-slug
            if (
                len(parts) == 3
                and parts[0] == brand_slug
                and parts[1] == col_slug
            ):
                ref_slug = parts[2]
                ref_code = _ref_from_slug(ref_slug)

                if ref_code in seen_refs:
                    continue
                seen_refs.add(ref_code)
                new_on_page += 1

                ref_url = f"{BASE_URL}/{brand_slug}/{col_slug}/{ref_slug}"
                entry = _scrape_ref_page(ref_url, brand_name, collection["name"], ref_code)
                if entry:
                    # Rimuovi campo interno prima di aggiungere
                    entry.pop("_wb_url", None)
                    results.append(entry)

                if len(results) >= max_refs:
                    break

                time.sleep(0.3)  # gentile con il server

        # Se non ci sono nuovi link, siamo arrivati all'ultima pagina
        if new_on_page == 0:
            break

        # Controlla se esiste "next page" link
        has_next = bool(soup.select_one(f'a[href*="?p={page+1}"], a[href*="/page/{page+1}"]'))
        if not has_next and new_on_page == 0:
            break
        page += 1

    log.info(f"    {collection['name']}: {len(results)} referenze")
    return results
