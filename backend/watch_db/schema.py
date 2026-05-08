"""
Master Watch Database — schema SQLite e init.

Tabella watch_references: fonte di verità per ogni referenza canonica.
Alimentata da catalog/watches.json + aliases.py + price_ranges.
"""

import sqlite3
import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("watch_db")

DB_PATH = Path(__file__).parent.parent / "data" / "watches.db"
CATALOG_PATH = Path(__file__).parent.parent / "catalog" / "watches.json"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = _connect()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS watch_references (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                brand           TEXT    NOT NULL,
                model           TEXT    NOT NULL,
                reference       TEXT    NOT NULL UNIQUE,
                reference_norm  TEXT    NOT NULL,
                canonical_name  TEXT    NOT NULL,
                year_from       INTEGER,
                year_to         INTEGER,
                case_size_mm    REAL,
                case_material   TEXT,
                movement        TEXT,
                avg_price_eur   REAL,
                price_min_eur   REAL,
                price_max_eur   REAL,
                image_url       TEXT,
                tags            TEXT,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS watch_aliases (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                reference_norm  TEXT    NOT NULL,
                alias           TEXT    NOT NULL,
                UNIQUE(reference_norm, alias)
            );

            CREATE INDEX IF NOT EXISTS idx_ref_norm
                ON watch_references(reference_norm);
            CREATE INDEX IF NOT EXISTS idx_alias
                ON watch_aliases(alias);
        """)
    conn.close()
    logger.debug("watch_db schema OK")


def _norm(ref: str) -> str:
    return ref.upper().replace(" ", "").replace("/", "").replace("-", "").replace(".", "")


def populate_from_catalog():
    """Carica watches.json + aliases.py nel DB. Idempotente."""
    from watch_db.aliases import ALIAS_MAP

    if not CATALOG_PATH.exists():
        logger.warning(f"Catalog non trovato: {CATALOG_PATH}")
        return

    watches = json.loads(CATALOG_PATH.read_text())
    conn = _connect()

    # Price range heuristic: ±25% dell'avg_price
    inserted = 0
    with conn:
        for w in watches:
            ref = w.get("reference", "").strip()
            if not ref:
                continue
            norm = _norm(ref)
            avg = w.get("avg_price_eur") or 0
            price_min = round(avg * 0.75) if avg else None
            price_max = round(avg * 1.35) if avg else None

            # Parse year range "2010-2020" or "2020-present"
            year_from = year_to = None
            yr = w.get("year_range", "")
            if yr:
                parts = yr.split("-")
                try:
                    year_from = int(parts[0])
                    year_to = None if parts[1].lower() in ("present", "oggi", "") else int(parts[1])
                except (IndexError, ValueError):
                    pass

            # case_size: "40mm" → 40.0
            case_mm = None
            cs = w.get("case_size", "")
            if cs:
                try:
                    case_mm = float(cs.replace("mm", "").strip())
                except ValueError:
                    pass

            tags_str = json.dumps(w.get("tags", []))

            conn.execute(
                """
                INSERT OR REPLACE INTO watch_references
                    (brand, model, reference, reference_norm, canonical_name,
                     year_from, year_to, case_size_mm, movement,
                     avg_price_eur, price_min_eur, price_max_eur, image_url, tags)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    w.get("brand", ""),
                    w.get("model", ""),
                    ref,
                    norm,
                    w.get("canonical_name", f"{w.get('brand','')} {w.get('model','')} {ref}"),
                    year_from,
                    year_to,
                    case_mm,
                    w.get("movement"),
                    avg if avg else None,
                    price_min,
                    price_max,
                    w.get("image_url"),
                    tags_str,
                ),
            )
            inserted += 1

        # Inserisci alias
        alias_count = 0
        for ref_norm, aliases in ALIAS_MAP.items():
            for alias in aliases:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO watch_aliases (reference_norm, alias) VALUES (?,?)",
                        (ref_norm, alias.lower().strip()),
                    )
                    alias_count += 1
                except Exception:
                    pass

    conn.close()
    logger.info(f"watch_db popolato: {inserted} referenze, {alias_count} alias")


def get_stats() -> dict:
    conn = _connect()
    refs = conn.execute("SELECT COUNT(*) FROM watch_references").fetchone()[0]
    aliases = conn.execute("SELECT COUNT(*) FROM watch_aliases").fetchone()[0]
    brands = conn.execute("SELECT COUNT(DISTINCT brand) FROM watch_references").fetchone()[0]
    conn.close()
    return {"references": refs, "aliases": aliases, "brands": brands}
