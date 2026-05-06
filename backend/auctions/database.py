"""
SQLite database per i risultati d'asta mondiali.
DB path: backend/data/auctions.db
"""
import sqlite3
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("auctions")

DB_PATH = Path(__file__).parent.parent / "data" / "auctions.db"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crea le tabelle se non esistono."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS auction_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                -- Casa d'aste
                auction_house TEXT NOT NULL,
                sale_name TEXT,
                sale_location TEXT,
                sale_date TEXT NOT NULL,
                lot_number TEXT,
                -- Orologio
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                reference TEXT,
                description TEXT,
                year_made TEXT,
                condition TEXT,
                -- Prezzi
                estimate_low_chf REAL,
                estimate_high_chf REAL,
                hammer_price_chf REAL,
                buyer_premium_pct REAL DEFAULT 26.0,
                total_price_chf REAL,
                currency TEXT DEFAULT 'CHF',
                -- Metadati
                lot_url TEXT,
                image_url TEXT,
                notes TEXT,
                is_record BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ar_reference
            ON auction_results (reference)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ar_brand_date
            ON auction_results (brand, sale_date)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ar_house_date
            ON auction_results (auction_house, sale_date)
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS auction_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL,
                brand TEXT NOT NULL,
                calculation_date TEXT NOT NULL,
                total_lots INTEGER,
                avg_hammer_to_estimate_ratio REAL,
                sell_through_rate REAL,
                price_trend_12m REAL,
                price_trend_36m REAL,
                sentiment_score REAL,
                sentiment_label TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_as_reference
            ON auction_sentiment (reference, calculation_date)
        """)
        conn.commit()
    logger.info(f"Database aste inizializzato: {DB_PATH}")


# ---------------------------------------------------------------------------
# CRUD auction_results
# ---------------------------------------------------------------------------

def insert_result(data: dict) -> int:
    """Inserisce un risultato d'asta. Ritorna l'id inserito."""
    fields = [
        "auction_house", "sale_name", "sale_location", "sale_date", "lot_number",
        "brand", "model", "reference", "description", "year_made", "condition",
        "estimate_low_chf", "estimate_high_chf", "hammer_price_chf",
        "buyer_premium_pct", "total_price_chf", "currency",
        "lot_url", "image_url", "notes", "is_record",
    ]
    cols = [f for f in fields if f in data]
    placeholders = ", ".join(["?"] * len(cols))
    values = [data[c] for c in cols]
    sql = f"INSERT INTO auction_results ({', '.join(cols)}) VALUES ({placeholders})"
    with _get_conn() as conn:
        cur = conn.execute(sql, values)
        conn.commit()
        return cur.lastrowid


def bulk_insert_results(rows: list[dict]) -> int:
    """Inserimento massivo. Salta duplicati (stesso house+sale_date+lot_number)."""
    inserted = 0
    with _get_conn() as conn:
        for data in rows:
            # Verifica duplicato
            existing = conn.execute(
                """SELECT id FROM auction_results
                   WHERE auction_house=? AND sale_date=? AND lot_number=?""",
                (data.get("auction_house"), data.get("sale_date"), data.get("lot_number")),
            ).fetchone()
            if existing:
                continue

            fields = [
                "auction_house", "sale_name", "sale_location", "sale_date", "lot_number",
                "brand", "model", "reference", "description", "year_made", "condition",
                "estimate_low_chf", "estimate_high_chf", "hammer_price_chf",
                "buyer_premium_pct", "total_price_chf", "currency",
                "lot_url", "image_url", "notes", "is_record",
            ]
            cols = [f for f in fields if f in data]
            placeholders = ", ".join(["?"] * len(cols))
            values = [data[c] for c in cols]
            sql = f"INSERT INTO auction_results ({', '.join(cols)}) VALUES ({placeholders})"
            conn.execute(sql, values)
            inserted += 1
        conn.commit()
    return inserted


def get_results_by_reference(
    reference: str,
    limit: int = 20,
    sort_by: str = "date",
) -> list[dict]:
    """Tutti i risultati per una referenza, ordinati."""
    order_map = {
        "date": "sale_date DESC",
        "price": "hammer_price_chf DESC",
        "performance": "(hammer_price_chf / NULLIF((estimate_low_chf + estimate_high_chf) / 2, 0)) DESC",
    }
    order = order_map.get(sort_by, "sale_date DESC")
    with _get_conn() as conn:
        rows = conn.execute(
            f"""SELECT * FROM auction_results
                WHERE reference = ?
                ORDER BY {order}
                LIMIT ?""",
            (reference, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def get_results_by_brand(brand: str, limit: int = 50) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM auction_results
               WHERE brand = ?
               ORDER BY sale_date DESC
               LIMIT ?""",
            (brand, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def get_records(brand: str | None = None, limit: int = 10) -> list[dict]:
    """Risultati segnati come record d'asta."""
    with _get_conn() as conn:
        if brand:
            rows = conn.execute(
                """SELECT * FROM auction_results
                   WHERE is_record = 1 AND brand = ?
                   ORDER BY hammer_price_chf DESC
                   LIMIT ?""",
                (brand, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM auction_results
                   WHERE is_record = 1
                   ORDER BY hammer_price_chf DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


def get_all_auction_houses() -> list[dict]:
    """Statistiche aggregate per casa d'aste."""
    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT
                   auction_house,
                   COUNT(*) AS total_lots,
                   MIN(sale_date) AS first_sale,
                   MAX(sale_date) AS last_sale,
                   ROUND(AVG(hammer_price_chf), 0) AS avg_hammer_chf,
                   ROUND(MAX(hammer_price_chf), 0) AS max_hammer_chf,
                   COUNT(DISTINCT sale_name) AS total_sales
               FROM auction_results
               GROUP BY auction_house
               ORDER BY total_lots DESC"""
        ).fetchall()
    return [dict(r) for r in rows]


def get_recent_results(limit: int = 20) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM auction_results
               ORDER BY sale_date DESC, id DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def count_results() -> int:
    with _get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM auction_results").fetchone()[0]


# ---------------------------------------------------------------------------
# CRUD auction_sentiment
# ---------------------------------------------------------------------------

def upsert_sentiment(data: dict) -> None:
    """Inserisce o aggiorna il sentiment per una referenza."""
    with _get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO auction_sentiment
               (reference, brand, calculation_date, total_lots,
                avg_hammer_to_estimate_ratio, sell_through_rate,
                price_trend_12m, price_trend_36m,
                sentiment_score, sentiment_label, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["reference"],
                data["brand"],
                data["calculation_date"],
                data.get("total_lots"),
                data.get("avg_hammer_to_estimate_ratio"),
                data.get("sell_through_rate"),
                data.get("price_trend_12m"),
                data.get("price_trend_36m"),
                data.get("sentiment_score"),
                data.get("sentiment_label"),
                data.get("notes"),
            ),
        )
        conn.commit()


def get_sentiment(reference: str) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute(
            """SELECT * FROM auction_sentiment
               WHERE reference = ?
               ORDER BY calculation_date DESC
               LIMIT 1""",
            (reference,),
        ).fetchone()
    return dict(row) if row else None


# Inizializza DB al momento dell'import
init_db()
