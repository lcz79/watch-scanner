"""
SQLite storage per Instagram Stories listings.
Tabella: story_listings con deduplicazione.
"""
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("stories.storage")

DB_PATH = Path(__file__).parent.parent.parent / "data" / "stories.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS story_listings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT NOT NULL,
                price       REAL NOT NULL,
                currency    TEXT DEFAULT 'EUR',
                brand       TEXT,
                reference   TEXT,
                condition   TEXT DEFAULT 'unknown',
                text_raw    TEXT,
                image_path  TEXT,
                post_url    TEXT,
                confidence  REAL DEFAULT 0.0,
                ocr_text    TEXT,
                captured_at TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_story_user_time ON story_listings (username, captured_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_story_ref ON story_listings (reference)"
        )
        conn.commit()


def is_duplicate(username: str, price: float, window_hours: int = 6) -> bool:
    """
    Controlla se esiste già un listing simile nelle ultime N ore
    (stesso utente, prezzo entro ±5%).
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()
    with _conn() as conn:
        row = conn.execute(
            """SELECT id FROM story_listings
               WHERE username=? AND captured_at > ?
               AND price BETWEEN ? AND ?""",
            (username, cutoff, price * 0.95, price * 1.05),
        ).fetchone()
    return row is not None


def save_listing(data: dict) -> bool:
    """
    Salva un listing se non è un duplicato.
    Ritorna True se salvato, False se duplicato/scartato.
    """
    username = data.get("username", "")
    price = data.get("price", 0)

    if is_duplicate(username, price):
        logger.debug(f"Duplicato @{username} {price}€ — skip")
        return False

    now = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            """INSERT INTO story_listings
               (username, price, currency, brand, reference, condition,
                text_raw, image_path, post_url, confidence, ocr_text,
                captured_at, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                username,
                price,
                data.get("currency", "EUR"),
                data.get("brand"),
                data.get("reference"),
                data.get("condition", "unknown"),
                data.get("text_raw", ""),
                data.get("image_path", ""),
                data.get("post_url", ""),
                data.get("confidence", 0.0),
                data.get("ocr_text", ""),
                data.get("timestamp", now),
                now,
            ),
        )
        conn.commit()

    logger.info(f"Story salvata: @{username} | {price}€ | ref={data.get('reference')} | conf={data.get('confidence'):.2f}")
    return True


def get_stories_for_reference(reference: str, hours: int = 48) -> list[dict]:
    """Recupera stories degli ultimi N ore per una referenza."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    ref_clean = reference.replace(" ", "").upper()

    with _conn() as conn:
        rows = conn.execute(
            """SELECT * FROM story_listings
               WHERE captured_at > ?
               AND (UPPER(REPLACE(reference, ' ', '')) LIKE ?
                    OR text_raw LIKE ?)
               ORDER BY captured_at DESC""",
            (cutoff, f"%{ref_clean}%", f"%{reference.upper()}%"),
        ).fetchall()

    return [dict(r) for r in rows]


def get_recent_stories(hours: int = 48) -> list[dict]:
    """Recupera tutte le stories recenti."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM story_listings WHERE captured_at > ? ORDER BY captured_at DESC",
            (cutoff,),
        ).fetchall()
    return [dict(r) for r in rows]


# Init automatico all'import
init_db()
