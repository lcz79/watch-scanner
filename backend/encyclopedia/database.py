"""
SQLite database per l'enciclopedia degli orologi di lusso.
Database path: backend/data/encyclopedia.db
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from utils.logger import get_logger

logger = get_logger("encyclopedia.database")

DB_PATH = Path(__file__).parent.parent / "data" / "encyclopedia.db"


def init_db() -> None:
    """Inizializza il database creando le tabelle se non esistono."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS watch_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                reference TEXT NOT NULL UNIQUE,
                collection TEXT,
                year_introduced INTEGER,
                year_discontinued INTEGER,
                case_material TEXT,
                case_diameter_mm REAL,
                case_thickness_mm REAL,
                water_resistance_m INTEGER,
                movement_type TEXT,
                movement_caliber TEXT,
                power_reserve_h INTEGER,
                frequency_vph INTEGER,
                jewels INTEGER,
                dial_color TEXT,
                dial_material TEXT,
                bracelet_type TEXT,
                clasp_type TEXT,
                retail_price_eur REAL,
                avg_market_price_eur REAL,
                description TEXT,
                technical_notes TEXT,
                is_discontinued BOOLEAN DEFAULT 0,
                is_limited_edition BOOLEAN DEFAULT 0,
                production_numbers INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS watch_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT,
                is_primary BOOLEAN DEFAULT 0,
                local_path TEXT,
                FOREIGN KEY (reference) REFERENCES watch_references(reference)
            );

            CREATE TABLE IF NOT EXISTS watch_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_reference TEXT NOT NULL,
                variant_reference TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (parent_reference) REFERENCES watch_references(reference)
            );

            CREATE TABLE IF NOT EXISTS watch_stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL,
                category TEXT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_url TEXT,
                FOREIGN KEY (reference) REFERENCES watch_references(reference)
            );

            CREATE INDEX IF NOT EXISTS idx_watch_brand ON watch_references(brand);
            CREATE INDEX IF NOT EXISTS idx_watch_model ON watch_references(model);
            CREATE INDEX IF NOT EXISTS idx_watch_collection ON watch_references(collection);
            CREATE INDEX IF NOT EXISTS idx_stories_reference ON watch_stories(reference);
            CREATE INDEX IF NOT EXISTS idx_variants_parent ON watch_variants(parent_reference);
        """)
        conn.commit()
    logger.info(f"Database enciclopedia inizializzato: {DB_PATH}")


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager per connessioni al database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def insert_watch(data: dict) -> bool:
    """Inserisce o aggiorna un orologio nel database. Ritorna True se inserito, False se aggiornato."""
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM watch_references WHERE reference = ?",
            (data["reference"],)
        ).fetchone()

        fields = [
            "brand", "model", "reference", "collection", "year_introduced", "year_discontinued",
            "case_material", "case_diameter_mm", "case_thickness_mm", "water_resistance_m",
            "movement_type", "movement_caliber", "power_reserve_h", "frequency_vph", "jewels",
            "dial_color", "dial_material", "bracelet_type", "clasp_type",
            "retail_price_eur", "avg_market_price_eur",
            "description", "technical_notes",
            "is_discontinued", "is_limited_edition", "production_numbers",
        ]
        values = {f: data.get(f) for f in fields}

        if existing:
            set_clause = ", ".join(f"{f} = :{f}" for f in fields if f != "reference")
            set_clause += ", updated_at = CURRENT_TIMESTAMP"
            conn.execute(
                f"UPDATE watch_references SET {set_clause} WHERE reference = :reference",
                values
            )
            conn.commit()
            return False
        else:
            placeholders = ", ".join(f":{f}" for f in fields)
            col_names = ", ".join(fields)
            conn.execute(
                f"INSERT INTO watch_references ({col_names}) VALUES ({placeholders})",
                values
            )
            conn.commit()
            return True


def insert_story(reference: str, category: str, title: str, content: str, source_url: str | None = None) -> None:
    """Inserisce una storia/curiosità per un orologio (se non esiste già)."""
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM watch_stories WHERE reference = ? AND title = ?",
            (reference, title)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO watch_stories (reference, category, title, content, source_url) VALUES (?, ?, ?, ?, ?)",
                (reference, category, title, content, source_url)
            )
            conn.commit()


def insert_variant(parent_reference: str, variant_reference: str, description: str | None = None) -> None:
    """Inserisce una variante (se non esiste già)."""
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM watch_variants WHERE parent_reference = ? AND variant_reference = ?",
            (parent_reference, variant_reference)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO watch_variants (parent_reference, variant_reference, description) VALUES (?, ?, ?)",
                (parent_reference, variant_reference, description)
            )
            conn.commit()


def insert_image(reference: str, url: str, source: str | None = None, is_primary: bool = False) -> None:
    """Inserisce un'immagine (se non esiste già)."""
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM watch_images WHERE reference = ? AND url = ?",
            (reference, url)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO watch_images (reference, url, source, is_primary) VALUES (?, ?, ?, ?)",
                (reference, url, source, is_primary)
            )
            conn.commit()


def get_watch_by_reference(reference: str) -> dict | None:
    """Recupera un orologio completo con varianti, storie e immagini."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM watch_references WHERE reference = ?",
            (reference,)
        ).fetchone()
        if not row:
            return None

        watch = dict(row)

        watch["images"] = [
            dict(r) for r in conn.execute(
                "SELECT * FROM watch_images WHERE reference = ? ORDER BY is_primary DESC",
                (reference,)
            ).fetchall()
        ]

        watch["variants"] = [
            dict(r) for r in conn.execute(
                "SELECT * FROM watch_variants WHERE parent_reference = ?",
                (reference,)
            ).fetchall()
        ]

        watch["stories"] = [
            dict(r) for r in conn.execute(
                "SELECT * FROM watch_stories WHERE reference = ? ORDER BY category",
                (reference,)
            ).fetchall()
        ]

        return watch


def search_watches(
    brand: str | None = None,
    model: str | None = None,
    reference: str | None = None,
    collection: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Ricerca orologi nel database con filtri multipli."""
    conditions = []
    params: list = []

    if brand:
        conditions.append("LOWER(brand) LIKE ?")
        params.append(f"%{brand.lower()}%")
    if model:
        conditions.append("LOWER(model) LIKE ?")
        params.append(f"%{model.lower()}%")
    if reference:
        conditions.append("LOWER(reference) LIKE ?")
        params.append(f"%{reference.lower()}%")
    if collection:
        conditions.append("LOWER(collection) LIKE ?")
        params.append(f"%{collection.lower()}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_db() as conn:
        rows = conn.execute(
            f"SELECT * FROM watch_references {where} ORDER BY brand, model LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()
        return [dict(r) for r in rows]


def get_brand_catalog(brand: str) -> list[dict]:
    """Tutti gli orologi di un brand."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM watch_references WHERE LOWER(brand) = LOWER(?) ORDER BY collection, model",
            (brand,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_popular_references(limit: int = 20) -> list[dict]:
    """Referenze più importanti ordinate per prezzo di mercato (proxy di notorietà)."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT wr.*, COUNT(ws.id) as story_count
               FROM watch_references wr
               LEFT JOIN watch_stories ws ON wr.reference = ws.reference
               GROUP BY wr.reference
               ORDER BY story_count DESC, wr.avg_market_price_eur DESC NULLS LAST
               LIMIT ?""",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def count_watches() -> int:
    """Conta il numero di orologi nel database."""
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) as cnt FROM watch_references").fetchone()
        return row["cnt"] if row else 0


def get_all_brands() -> list[str]:
    """Lista tutti i brand presenti nel database."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT brand FROM watch_references ORDER BY brand"
        ).fetchall()
        return [r["brand"] for r in rows]
