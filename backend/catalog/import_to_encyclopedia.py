"""
Importa watches.json nel database SQLite dell'enciclopedia.
Parsa case_size, year_range e movement nei campi strutturati del DB.

Uso:
  python3 import_to_encyclopedia.py          # importa tutto
  python3 import_to_encyclopedia.py --dry    # mostra stats senza scrivere
"""
import json, re, sys, pathlib, logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s — %(message)s")
log = logging.getLogger("import")

HERE        = pathlib.Path(__file__).parent
CATALOG     = HERE / "watches.json"
BACKEND_DIR = HERE.parent
sys.path.insert(0, str(BACKEND_DIR))


def parse_diameter(case_size: str | None) -> float | None:
    if not case_size:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*mm", case_size, re.I)
    return float(m.group(1)) if m else None


def parse_year_range(year_range: str | None) -> tuple[int | None, int | None, bool]:
    """Ritorna (year_introduced, year_discontinued, is_discontinued)."""
    if not year_range:
        return None, None, False
    # "2016–2022" or "2016-2022"
    m = re.match(r"(\d{4})[–\-](\d{4})", year_range)
    if m:
        return int(m.group(1)), int(m.group(2)), True
    # "2016–present" or "2016-present"
    m = re.match(r"(\d{4})[–\-](?:present|oggi|current)", year_range, re.I)
    if m:
        return int(m.group(1)), None, False
    # Solo anno "2016"
    m = re.match(r"(\d{4})$", year_range.strip())
    if m:
        return int(m.group(1)), None, False
    return None, None, False


def catalog_to_db_record(w: dict) -> dict:
    diam = parse_diameter(w.get("case_size"))
    year_in, year_disc, is_disc = parse_year_range(w.get("year_range"))
    avg_price = w.get("avg_price_eur") or 0

    return {
        "brand":             w["brand"],
        "model":             w["model"],
        "reference":         w["reference"],
        "collection":        w.get("model"),    # usa model come collezione
        "year_introduced":   year_in,
        "year_discontinued": year_disc,
        "case_diameter_mm":  diam,
        "movement_caliber":  w.get("movement") or None,
        "avg_market_price_eur": avg_price if avg_price > 0 else None,
        "is_discontinued":   1 if is_disc else 0,
        "is_limited_edition": 0,
    }


def run(dry: bool = False) -> dict:
    from encyclopedia.database import init_db, insert_watch, insert_image, count_watches

    if not CATALOG.exists():
        log.error(f"watches.json non trovato: {CATALOG}")
        return {}

    watches = json.loads(CATALOG.read_text())
    log.info(f"Catalogo: {len(watches)} referenze")

    init_db()
    before = count_watches()
    log.info(f"Encyclopedia DB prima: {before} referenze")

    inserted = updated = skipped = 0
    for w in watches:
        if not w.get("reference") or not w.get("brand"):
            skipped += 1
            continue

        record = catalog_to_db_record(w)

        if not dry:
            is_new = insert_watch(record)
            if is_new:
                inserted += 1
                img = w.get("image_url", "")
                if img and "referral" not in img and "ebay" not in img:
                    insert_image(w["reference"], img, source="watchbase", is_primary=True)
            else:
                updated += 1
        else:
            inserted += 1  # dry: count as would-insert

    after = count_watches() if not dry else before + inserted
    log.info(
        f"{'[DRY] ' if dry else ''}Inseriti: {inserted} | Aggiornati: {updated} | "
        f"Saltati: {skipped} | Totale DB: {after}"
    )
    return {"inserted": inserted, "updated": updated, "skipped": skipped, "total": after}


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    run(dry=dry)
