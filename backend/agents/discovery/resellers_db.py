"""
Database SQLite centralizzato dei reseller scoperti.
Condiviso da tutti i discovery agent.

Tabelle:
  - dealers        : account analizzati con score e metadati
  - relationships  : connessioni tra account (following, mentioned, ...)
  - crawl_logs     : log delle operazioni di crawl

Il file DB è in backend/data/resellers.db.
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("resellers_db")

DB_PATH = Path(__file__).parent.parent.parent / "data" / "resellers.db"

# Keyword nella bio/descrizione account che indicano un reseller
BIO_KEYWORDS = [
    "reseller", "dealer", "trader", "vendita", "vendo", "for sale",
    "compro", "vends", "achat", "buy", "sell", "orologio", "watch",
    "timepiece", "dm for price", "dm per prezzo", "available",
    "disponibile", "preloved", "pre-owned", "preowned", "second hand",
    "usato", "luxury", "lusso", "rolex", "patek", "audemars", "omega",
    "tudor", "boutique", "certified", "orologi", "montres", "relojes",
]

# Keyword nei post che indicano annuncio di vendita
SALE_KEYWORDS = [
    "vendo", "vendesi", "for sale", "forsale", "prezzo", "price",
    "asking", "dm", "available", "disponibile", "€", "euro",
    "box and papers", "full set", "con scatola", "sold", "venduto",
]

PRICE_RE = re.compile(r'[\d\.]+\s*[€$]|[€$]\s*[\d\.]+|\d{4,6}\s*euro', re.I)

# Score minimo per essere considerato reseller
MIN_SCORE = 3


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Crea le tabelle se non esistono."""
    conn = _connect()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS dealers (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT    NOT NULL UNIQUE,
                platform        TEXT    NOT NULL DEFAULT 'instagram',
                bio             TEXT,
                website         TEXT,
                is_dealer       BOOLEAN,
                confidence      REAL,
                score           REAL    NOT NULL DEFAULT 0,
                followers_count INTEGER,
                post_count      INTEGER,
                cms_type        TEXT,
                last_crawled    TIMESTAMP,
                created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS relationships (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                source_username TEXT    NOT NULL,
                target_username TEXT    NOT NULL,
                relation_type   TEXT    NOT NULL,
                created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_username, target_username, relation_type)
            );

            CREATE TABLE IF NOT EXISTS crawl_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL,
                source      TEXT    NOT NULL,
                status      TEXT    NOT NULL,
                message     TEXT    NOT NULL DEFAULT '',
                created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.close()
    logger.debug(f"DB inizializzato: {DB_PATH}")


def upsert_dealer(data: dict):
    """
    Inserisce un nuovo dealer o aggiorna quello esistente.

    Campi supportati in data:
      username, platform, bio, website, is_dealer, confidence, score,
      followers_count, post_count, cms_type, last_crawled
    """
    if not data.get("username"):
        raise ValueError("upsert_dealer: 'username' è obbligatorio")

    now = datetime.now().isoformat()
    fields = [
        "username", "platform", "bio", "website", "is_dealer",
        "confidence", "score", "followers_count", "post_count",
        "cms_type", "last_crawled",
    ]
    # Filtra solo i campi presenti in data
    present = {k: data[k] for k in fields if k in data}
    present.setdefault("platform", "instagram")
    present["updated_at"] = now

    columns = list(present.keys())
    placeholders = ", ".join("?" * len(columns))
    col_list = ", ".join(columns)
    updates = ", ".join(f"{c}=excluded.{c}" for c in columns if c != "username")

    sql = f"""
        INSERT INTO dealers ({col_list}, created_at)
        VALUES ({placeholders}, ?)
        ON CONFLICT(username) DO UPDATE SET {updates}
    """
    values = [present[c] for c in columns] + [now]

    conn = _connect()
    with conn:
        conn.execute(sql, values)
    conn.close()
    logger.debug(f"upsert_dealer: @{data['username']} salvato")


def get_all_resellers(min_score: float = 0, platform: str = None) -> list[dict]:
    """
    Restituisce tutti i dealer con score >= min_score.
    Filtra opzionalmente per piattaforma.

    Ogni dict contiene: username, platform, website, score, is_dealer.
    """
    conn = _connect()
    if platform:
        rows = conn.execute(
            "SELECT username, platform, website, score, is_dealer "
            "FROM dealers WHERE score >= ? AND platform = ? ORDER BY score DESC",
            (min_score, platform),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT username, platform, website, score, is_dealer "
            "FROM dealers WHERE score >= ? ORDER BY score DESC",
            (min_score,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_classification() -> list[dict]:
    """Restituisce i dealer senza classificazione (is_dealer IS NULL)."""
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM dealers WHERE is_dealer IS NULL ORDER BY created_at ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_website_crawl() -> list[dict]:
    """Restituisce i dealer con website valorizzato ma non ancora crawlati."""
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM dealers "
        "WHERE website IS NOT NULL AND website != '' AND last_crawled IS NULL "
        "ORDER BY score DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_crawl(username: str, source: str, status: str, message: str = ""):
    """Registra un'operazione di crawl nella tabella crawl_logs."""
    conn = _connect()
    with conn:
        conn.execute(
            "INSERT INTO crawl_logs (username, source, status, message) VALUES (?, ?, ?, ?)",
            (username, source, status, message),
        )
    conn.close()


# ── Helpers compatibili con il vecchio JSON-based API ────────────────────────

def score_account(bio: str, recent_captions: list, followers: int, following: int) -> tuple:
    """
    Calcola uno score 0-10 per capire quanto è probabile che sia un reseller.
    Ritorna (score, motivi).
    """
    score = 0
    reasons = []
    bio_lower = (bio or "").lower()

    matches = [kw for kw in BIO_KEYWORDS if kw in bio_lower]
    bio_pts = min(len(matches), 4)
    if bio_pts:
        score += bio_pts
        reasons.append(f"bio: {matches[:3]}")

    if 500 < followers < 500_000:
        score += 1
        reasons.append(f"{followers:,} follower")

    if following > 0 and followers / following > 1.2:
        score += 1
        reasons.append("rapporto follower/following buono")

    if recent_captions:
        sale_count = sum(1 for c in recent_captions if any(kw in c.lower() for kw in SALE_KEYWORDS))
        price_count = sum(1 for c in recent_captions if PRICE_RE.search(c))

        if sale_count / len(recent_captions) > 0.25:
            score += 2
            reasons.append(f"{sale_count}/{len(recent_captions)} post vendita")
        if price_count > 0:
            score += 1
            reasons.append(f"{price_count} post con prezzi")

    return score, reasons


def add_reseller(db: dict, username: str, platform: str, score: int, reasons: list,
                 followers: int, bio: str, discovered_via: str, pk: str = "") -> bool:
    """
    Compatibilità con il vecchio API JSON-based.
    Inserisce/aggiorna nel DB SQLite e aggiorna anche il dict in-memory.
    """
    is_new = username not in db.get("resellers", {})

    upsert_dealer({
        "username": username,
        "platform": platform,
        "bio": (bio or "")[:500],
        "score": float(score),
        "followers_count": followers,
        "is_dealer": True if score >= MIN_SCORE else None,
        "confidence": min(1.0, score / 10.0),
    })

    if is_new or score > db.get("resellers", {}).get(username, {}).get("score", 0):
        db.setdefault("resellers", {})[username] = {
            "username": username,
            "platform": platform,
            "score": score,
            "reasons": reasons,
            "followers": followers,
            "bio": (bio or "")[:200],
            "pk": pk,
            "discovered_via": discovered_via,
            "discovered_at": datetime.now().isoformat(),
        }
        db.setdefault("stats", {})
        db["stats"][platform] = db["stats"].get(platform, 0) + (1 if is_new else 0)

    if is_new:
        logger.info(f"  + @{username} [{platform}] score={score} via {discovered_via} | {reasons[:2]}")

    return is_new


def blacklist(db: dict, username: str):
    """Compatibilità con il vecchio API: aggiunge alla blacklist in-memory e marca nel DB."""
    if username not in db.get("blacklist", []):
        db.setdefault("blacklist", []).append(username)
    upsert_dealer({"username": username, "is_dealer": False, "confidence": 0.0})


def is_known(db: dict, username: str) -> bool:
    """Compatibilità con il vecchio API: controlla se l'account è già nel DB."""
    return username in db.get("resellers", {}) or username in db.get("blacklist", [])


def load() -> dict:
    """
    Compatibilità con il vecchio API: carica i dati dal DB SQLite
    e li restituisce nel formato dict usato dai discovery agent legacy.
    """
    init_db()
    conn = _connect()
    rows = conn.execute("SELECT * FROM dealers").fetchall()
    conn.close()

    resellers = {}
    blacklisted = []
    stats: dict = {}

    for row in rows:
        d = dict(row)
        username = d["username"]
        platform = d.get("platform", "instagram")

        if d.get("is_dealer") is False:
            blacklisted.append(username)
        else:
            resellers[username] = {
                "username": username,
                "platform": platform,
                "score": d.get("score", 0),
                "followers": d.get("followers_count", 0),
                "bio": d.get("bio", ""),
                "website": d.get("website", ""),
                "discovered_at": d.get("created_at", ""),
            }
            stats[platform] = stats.get(platform, 0) + 1

    return {
        "resellers": resellers,
        "blacklist": blacklisted,
        "stats": stats,
        "last_updated": datetime.now().isoformat(),
    }


def save(db: dict):
    """
    Compatibilità con il vecchio API: persiste il dict in-memory nel DB SQLite.
    I dati vengono già scritti on-the-fly da add_reseller/blacklist,
    quindi questa funzione fa solo un flush dei record non ancora presenti.
    """
    for username, info in db.get("resellers", {}).items():
        upsert_dealer({
            "username": username,
            "platform": info.get("platform", "instagram"),
            "bio": info.get("bio", ""),
            "website": info.get("website", ""),
            "score": float(info.get("score", 0)),
            "followers_count": info.get("followers", 0),
        })
    for username in db.get("blacklist", []):
        upsert_dealer({"username": username, "is_dealer": False, "confidence": 0.0})


def get_stats() -> dict:
    """Compatibilità con il vecchio API: restituisce statistiche aggregate."""
    conn = _connect()
    total = conn.execute("SELECT COUNT(*) FROM dealers").fetchone()[0]
    blacklisted = conn.execute(
        "SELECT COUNT(*) FROM dealers WHERE is_dealer = 0"
    ).fetchone()[0]
    by_platform_rows = conn.execute(
        "SELECT platform, COUNT(*) as cnt FROM dealers WHERE is_dealer != 0 OR is_dealer IS NULL "
        "GROUP BY platform"
    ).fetchall()
    top_rows = conn.execute(
        "SELECT username, platform, score, website FROM dealers ORDER BY score DESC LIMIT 10"
    ).fetchall()
    conn.close()

    by_platform = {r["platform"]: r["cnt"] for r in by_platform_rows}
    top_10 = [dict(r) for r in top_rows]

    return {
        "total": total,
        "by_platform": by_platform,
        "blacklisted": blacklisted,
        "last_updated": datetime.now().isoformat(),
        "top_10": top_10,
    }


# Inizializza il DB all'import
init_db()
