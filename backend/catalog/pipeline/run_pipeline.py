#!/usr/bin/env python3
"""
Entry-point principale del pipeline.

Uso:
  python3 run_pipeline.py                  # scraping completo
  python3 run_pipeline.py --brand rolex    # solo un brand
  python3 run_pipeline.py --dry-run        # mostra cosa farebbe senza scrivere
  python3 run_pipeline.py --merge-only     # solo merge + export senza scraping

Output:
  ../watches_full.json   — tutti i record scraped
  ../watches.json        — merged con catalogo manuale esistente
"""
import argparse, json, logging, pathlib, sys, time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline")

# Aggiunge la dir corrente al path per importare i moduli locali
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from config import BRANDS, DELAY_BETWEEN_BRANDS
from brand_spider import get_collections
from reference_spider import get_references
from normalize import normalize_entry, merge_with_existing, dedup_and_sort

HERE       = pathlib.Path(__file__).parent
FULL_JSON  = HERE.parent / "watches_full.json"
FINAL_JSON = HERE.parent / "watches.json"
PROGRESS   = HERE / ".progress.json"


def load_progress() -> dict:
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text())
    return {}


def save_progress(state: dict):
    PROGRESS.write_text(json.dumps(state, indent=2))


def run_scraping(target_brand_slug: str | None, dry_run: bool) -> list[dict]:
    progress = load_progress()
    all_entries: list[dict] = []

    # Carica lavoro già fatto in sessioni precedenti
    if FULL_JSON.exists():
        all_entries = json.loads(FULL_JSON.read_text())
        log.info(f"Caricati {len(all_entries)} record da sessione precedente")

    brands = BRANDS
    if target_brand_slug:
        brands = [(name, slug) for name, slug in BRANDS if slug == target_brand_slug]
        if not brands:
            log.error(f"Brand slug '{target_brand_slug}' non trovato in config.py")
            return all_entries

    for brand_name, brand_slug in brands:
        if brand_slug in progress.get("completed_brands", []):
            log.info(f"✓ {brand_name} già completato (skip)")
            continue

        log.info(f"\n── {brand_name} ({brand_slug}) ──")

        if dry_run:
            log.info("  [DRY RUN] skip fetch")
            continue

        collections = get_collections(brand_slug)

        # Se 0 collezioni → la pagina brand ha probabilmente restituito 429/403.
        # Non marchiamo come completato: il prossimo run riproverà.
        if not collections:
            log.warning(f"  Nessuna collezione trovata per {brand_name} — skip (verrà riprovato)")
            time.sleep(DELAY_BETWEEN_BRANDS)
            continue

        brand_entries: list[dict] = []
        for col in collections:
            refs = get_references(col, brand_name)
            for r in refs:
                normalized = normalize_entry(r)
                if normalized:
                    brand_entries.append(normalized)
            time.sleep(0.5)  # cortesia extra tra collection

        log.info(f"  → {len(brand_entries)} referenze per {brand_name}")
        all_entries.extend(brand_entries)

        # Salva stato intermedio — marca completato solo se abbiamo dati validi
        if not dry_run:
            FULL_JSON.write_text(json.dumps(all_entries, ensure_ascii=False, indent=2))
            completed = progress.get("completed_brands", [])
            completed.append(brand_slug)
            progress["completed_brands"] = completed
            save_progress(progress)

        time.sleep(DELAY_BETWEEN_BRANDS)

    return all_entries


def export_final(all_entries: list[dict]):
    """Merge con watches.json esistente e scrive il file finale."""
    log.info(f"\n── Export finale ──")
    merged = merge_with_existing(all_entries, FINAL_JSON)
    sorted_entries = dedup_and_sort(merged)
    FINAL_JSON.write_text(json.dumps(sorted_entries, ensure_ascii=False, indent=2))

    from collections import Counter
    counts = Counter(e.get("brand", "?") for e in sorted_entries)
    log.info(f"Totale: {len(sorted_entries)} referenze")
    for brand, n in sorted(counts.items(), key=lambda x: -x[1])[:20]:
        log.info(f"  {brand:<30} {n:>4}")

    return sorted_entries


def main():
    parser = argparse.ArgumentParser(description="Watch Reference Scraping Pipeline")
    parser.add_argument("--brand", help="Scraping solo per questo brand slug (es: rolex)")
    parser.add_argument("--dry-run", action="store_true", help="Simula senza fare fetch")
    parser.add_argument("--merge-only", action="store_true", help="Solo merge + export")
    parser.add_argument("--reset", action="store_true", help="Cancella cache progresso e riparte")
    args = parser.parse_args()

    if args.reset:
        if PROGRESS.exists():
            PROGRESS.unlink()
            log.info("Progress azzerato")
        if FULL_JSON.exists():
            FULL_JSON.unlink()
            log.info("watches_full.json eliminato")

    if args.merge_only:
        existing = json.loads(FULL_JSON.read_text()) if FULL_JSON.exists() else []
        export_final(existing)
        return

    all_entries = run_scraping(args.brand, args.dry_run)

    if not args.dry_run:
        export_final(all_entries)
        log.info(f"\n✓ Done. Output: {FINAL_JSON}")
    else:
        log.info("[DRY RUN] Nessun file scritto.")


if __name__ == "__main__":
    main()
