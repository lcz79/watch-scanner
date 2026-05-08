"""
Reference resolver — dato un testo libero, restituisce la referenza canonica.

Strategie in ordine di priorità:
  1. Match esatto della reference_norm nel DB
  2. Match alias esatto (es. "hulk" → 116610LV)
  3. Match parziale reference (es. "116610" → 116610LN o 116610LV)
  4. Match parziale su canonical_name (brand + model)
  5. None se nessun match con confidence sufficiente
"""

import re
import sqlite3
from watch_db.schema import _connect, _norm, init_db
from utils.logger import get_logger

logger = get_logger("watch_db.resolver")

# Rimuove parole rumore che non aiutano il match
_NOISE = re.compile(
    r'\b(rolex|patek|audemars|piguet|omega|tudor|iwc|panerai|cartier|breitling'
    r'|philippe|orologio|watch|ref|reference|rif|mod|modello|acciaio|steel'
    r'|oro|gold|usato|used|mint|excellent|buono|ottime|condizioni)\b',
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    """Normalizza il testo per la ricerca: lowercase, rimuovi rumore."""
    return _NOISE.sub("", text.lower()).strip()


def resolve_reference(query: str) -> dict | None:
    """
    Dato un testo libero (es. "Rolex Sub hulk", "116610LV", "batman gmt"),
    restituisce il dict della referenza canonica o None.

    Returns dict con: reference, reference_norm, brand, model, canonical_name,
                      avg_price_eur, price_min_eur, price_max_eur, confidence
    """
    if not query or not query.strip():
        return None

    conn = _connect()
    result = (
        _try_exact_norm(conn, query)
        or _try_alias_exact(conn, query)
        or _try_partial_ref(conn, query)
        or _try_alias_partial(conn, query)
        or _try_canonical_name(conn, query)
    )
    conn.close()
    return result


def _row_to_dict(row: sqlite3.Row, confidence: float) -> dict:
    d = dict(row)
    d["confidence"] = confidence
    return d


def _try_exact_norm(conn, query: str) -> dict | None:
    norm = _norm(query)
    row = conn.execute(
        "SELECT * FROM watch_references WHERE reference_norm = ?", (norm,)
    ).fetchone()
    if row:
        logger.debug(f"resolve '{query}' → exact norm match: {row['reference']}")
        return _row_to_dict(row, 1.0)
    return None


def _try_alias_exact(conn, query: str) -> dict | None:
    alias = query.lower().strip()
    row = conn.execute(
        """
        SELECT r.* FROM watch_references r
        JOIN watch_aliases a ON a.reference_norm = r.reference_norm
        WHERE a.alias = ?
        LIMIT 1
        """,
        (alias,),
    ).fetchone()
    if row:
        logger.debug(f"resolve '{query}' → alias exact: {row['reference']}")
        return _row_to_dict(row, 0.95)
    return None


def _try_partial_ref(conn, query: str) -> dict | None:
    # Cerca il testo normalizzato come sottostringa di reference_norm
    norm = _norm(query)
    if len(norm) < 4:
        return None
    rows = conn.execute(
        "SELECT * FROM watch_references WHERE reference_norm LIKE ? ORDER BY LENGTH(reference_norm) ASC LIMIT 3",
        (f"%{norm}%",),
    ).fetchall()
    if rows:
        logger.debug(f"resolve '{query}' → partial ref: {rows[0]['reference']}")
        return _row_to_dict(rows[0], 0.85)
    return None


def _try_alias_partial(conn, query: str) -> dict | None:
    cleaned = _clean(query)
    if len(cleaned) < 3:
        return None
    # Controlla se qualche alias è contenuto nel query o viceversa
    rows = conn.execute(
        """
        SELECT r.*, a.alias FROM watch_references r
        JOIN watch_aliases a ON a.reference_norm = r.reference_norm
        WHERE ? LIKE '%' || a.alias || '%'
           OR a.alias LIKE '%' || ? || '%'
        ORDER BY LENGTH(a.alias) DESC
        LIMIT 3
        """,
        (cleaned, cleaned),
    ).fetchall()
    if rows:
        logger.debug(f"resolve '{query}' → alias partial: {rows[0]['reference']} (via '{rows[0]['alias']}')")
        return _row_to_dict(rows[0], 0.80)
    return None


def _try_canonical_name(conn, query: str) -> dict | None:
    cleaned = _clean(query)
    words = [w for w in cleaned.split() if len(w) >= 3]
    if not words:
        return None
    # Almeno 2 parole significative devono matchare sul canonical_name
    like_parts = " AND ".join([f"LOWER(canonical_name) LIKE ?" for w in words])
    params = [f"%{w}%" for w in words]
    rows = conn.execute(
        f"SELECT * FROM watch_references WHERE {like_parts} LIMIT 3",
        params,
    ).fetchall()
    if rows:
        logger.debug(f"resolve '{query}' → canonical name: {rows[0]['reference']}")
        return _row_to_dict(rows[0], 0.70)
    return None


def get_price_range(reference: str) -> tuple[float | None, float | None]:
    """Restituisce (price_min_eur, price_max_eur) per la referenza data."""
    conn = _connect()
    norm = _norm(reference)
    row = conn.execute(
        "SELECT price_min_eur, price_max_eur FROM watch_references WHERE reference_norm = ?",
        (norm,),
    ).fetchone()
    conn.close()
    if row:
        return row["price_min_eur"], row["price_max_eur"]
    return None, None


def is_price_plausible(reference: str, price: float) -> bool:
    """True se il prezzo è nel range atteso ±50% per quella referenza."""
    p_min, p_max = get_price_range(reference)
    if p_min is None or p_max is None:
        return True  # senza dati, non scartare
    # tolleranza ampia: 50% sotto il min o 100% sopra il max → sospetto
    return (p_min * 0.5) <= price <= (p_max * 2.0)
