"""
Normalize: pulisce e standardizza i record scraped.
- De-duplica per (brand, reference)
- Normalizza codici referenza
- Rimuove record senza reference valida
- Merge con catalogo esistente (i dati manuali hanno priorità)
"""
import re, json, pathlib, logging

log = logging.getLogger("normalize")

_REF_CLEAN = re.compile(r"[\s–—]+")


def normalize_reference(ref: str) -> str:
    """Normalizza referenza per confronto: uppercase, no spazi/trattini doppi."""
    return _REF_CLEAN.sub("", ref).upper().strip()


def _is_valid_ref(ref: str) -> bool:
    """Filtra referenze palesemente invalide (troppo corte, generiche, ecc.)."""
    if not ref or len(ref) < 3:
        return False
    if ref.lower() in {"n/a", "none", "tbd", "ref", "ref.", "reference"}:
        return False
    # Deve contenere almeno un numero o essere un codice noto
    return bool(re.search(r"[0-9A-Z]", ref.upper()))


def normalize_entry(entry: dict) -> dict | None:
    """Normalizza un singolo record, ritorna None se invalido."""
    ref = entry.get("reference", "").strip()
    if not ref or not _is_valid_ref(ref):
        return None

    # Normalizza reference solo per uso interno, lascia il display come c'è
    brand = entry.get("brand", "").strip()
    model = entry.get("model", "").strip()
    if not brand or not model:
        return None

    # Crea ID deterministico e stabile
    id_brand = re.sub(r"[^a-z0-9]+", "-", brand.lower()).strip("-")
    id_ref   = re.sub(r"[^a-z0-9]+", "-", ref.lower()).strip("-")
    entry["id"] = f"{id_brand}-{id_ref}"

    # Canonical name
    entry["canonical_name"] = f"{brand} {model} {ref}"

    # Rimuovi campi interni
    for k in list(entry.keys()):
        if k.startswith("_"):
            entry.pop(k)

    # Default campi vuoti
    entry.setdefault("year_range", "")
    entry.setdefault("movement", "")
    entry.setdefault("case_size", "")
    entry.setdefault("image_url", "")
    entry.setdefault("tags", [])
    entry.setdefault("avg_price_eur", 0)

    return entry


def merge_with_existing(
    scraped: list[dict],
    existing_path: pathlib.Path,
) -> list[dict]:
    """
    Merge scraped + existing.
    Chiave di merge: (brand, normalize_reference(reference)).
    I record esistenti (curati a mano) hanno priorità su quelli scraped.
    I nuovi da scraping vengono aggiunti in coda.
    """
    existing: list[dict] = []
    if existing_path.exists():
        existing = json.loads(existing_path.read_text())

    # Indice existing per chiave
    existing_keys: dict[tuple, dict] = {}
    for e in existing:
        key = (e.get("brand", ""), normalize_reference(e.get("reference", "")))
        existing_keys[key] = e

    added = 0
    for entry in scraped:
        key = (entry.get("brand", ""), normalize_reference(entry.get("reference", "")))
        if key not in existing_keys:
            existing_keys[key] = entry
            added += 1

    log.info(f"Merge: {len(existing)} esistenti + {added} nuovi = {len(existing_keys)} totale")
    return list(existing_keys.values())


def dedup_and_sort(entries: list[dict]) -> list[dict]:
    """De-duplica e ordina per brand → model → reference."""
    seen = set()
    unique = []
    for e in entries:
        key = (e.get("brand", ""), normalize_reference(e.get("reference", "")))
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return sorted(unique, key=lambda x: (
        x.get("brand", ""),
        x.get("model", ""),
        x.get("reference", ""),
    ))
