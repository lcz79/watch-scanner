"""
Market Intelligence — 3 dynamic cards for the homepage.

Computes:
  - most_appreciated: reference with biggest % price gain in ~6 months
  - most_traded:      reference with most auction appearances
  - rarest:           reference with fewest active marketplace listings
"""
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

PH_DB = Path(__file__).parent.parent / "data" / "price_history.db"
AR_DB = Path(__file__).parent.parent / "data" / "auctions.db"

# Fallback brand/model info for references not yet in auction_results
REF_INFO: dict[str, tuple[str, str]] = {
    "116610LN":  ("Rolex",            "Submariner Date"),
    "5711/1A":   ("Patek Philippe",   "Nautilus"),
    "126710BLNR":("Rolex",            "GMT-Master II"),
    "15500ST":   ("Audemars Piguet",  "Royal Oak"),
    "16520":     ("Rolex",            "Daytona"),
    "6241":      ("Rolex",            "Daytona"),
    "2499":      ("Patek Philippe",   "Perpetual Calendar"),
    "5402ST":    ("Audemars Piguet",  "Royal Oak Jumbo"),
    "5726A":     ("Patek Philippe",   "Aquanaut Travel Time"),
    "6265":      ("Rolex",            "Daytona"),
    "RM 011":    ("Richard Mille",    "RM 011"),
    "RES":       ("F.P. Journe",      "Resonance"),
    "TN":        ("F.P. Journe",      "Tourbillon"),
    "W2006951":  ("Cartier",          "Santos"),
}


def _ph_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(PH_DB))
    conn.row_factory = sqlite3.Row
    return conn


def _ar_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(AR_DB))
    conn.row_factory = sqlite3.Row
    return conn


def _lookup_brand_model(reference: str, ar_cur: sqlite3.Cursor) -> tuple[str, str]:
    ar_cur.execute(
        "SELECT brand, model FROM auction_results WHERE reference=? AND brand != 'Unknown' LIMIT 1",
        (reference,),
    )
    row = ar_cur.fetchone()
    if row and row["brand"] and row["brand"] != "Unknown":
        return row["brand"], row["model"] or reference
    fallback = REF_INFO.get(reference)
    if fallback:
        return fallback
    return "Unknown", reference


def compute_market_intelligence() -> dict:
    """Main function — returns the market intelligence payload."""
    now = datetime.now(timezone.utc)
    six_months_ago = now - timedelta(days=180)
    date_6m = six_months_ago.strftime("%Y-%m-%d")

    ph = _ph_conn()
    ar = _ar_conn()
    ph_cur = ph.cursor()
    ar_cur = ar.cursor()

    try:
        # ── Collect all references with price history ────────────────────────
        ph_cur.execute("SELECT DISTINCT reference FROM price_snapshots")
        refs = [r[0] for r in ph_cur.fetchall()]

        appreciation_candidates = []
        for ref in refs:
            # latest snapshot
            ph_cur.execute(
                "SELECT median_price, date, sample_size FROM price_snapshots "
                "WHERE reference=? ORDER BY date DESC LIMIT 1",
                (ref,),
            )
            latest = ph_cur.fetchone()
            if not latest or not latest["median_price"]:
                continue

            # snapshot closest to 6 months ago (≤ date_6m)
            ph_cur.execute(
                "SELECT median_price, date FROM price_snapshots "
                "WHERE reference=? AND date <= ? ORDER BY date DESC LIMIT 1",
                (ref, date_6m),
            )
            past = ph_cur.fetchone()
            if not past or not past["median_price"] or past["median_price"] == 0:
                continue

            chg = (latest["median_price"] - past["median_price"]) / past["median_price"] * 100
            # compute actual days between the two snapshots
            try:
                d1 = datetime.fromisoformat(past["date"])
                d2 = datetime.fromisoformat(latest["date"])
                period_days = (d2 - d1).days
            except Exception:
                period_days = 180

            # Build sparkline: last 12 monthly snapshots
            ph_cur.execute(
                """
                SELECT strftime('%Y-%m', date) AS ym, AVG(median_price) AS mp
                FROM price_snapshots
                WHERE reference=?
                GROUP BY ym
                ORDER BY ym DESC
                LIMIT 12
                """,
                (ref,),
            )
            sparkline_rows = ph_cur.fetchall()
            sparkline = [round(float(r["mp"]), 2) for r in reversed(sparkline_rows)]

            appreciation_candidates.append({
                "reference": ref,
                "old_price": float(past["median_price"]),
                "new_price": float(latest["median_price"]),
                "change_pct": round(chg, 2),
                "period_days": period_days,
                "sample_size": latest["sample_size"] or 0,
                "sparkline": sparkline,
            })

        # ── most_appreciated ────────────────────────────────────────────────
        if not appreciation_candidates:
            most_appreciated = _empty_appreciation_card()
        else:
            best = max(appreciation_candidates, key=lambda x: x["change_pct"])
            brand, model = _lookup_brand_model(best["reference"], ar_cur)
            most_appreciated = {
                "has_data": True,
                "reference": best["reference"],
                "brand": brand,
                "model": model,
                "current_price_chf": best["new_price"],
                "price_6m_ago_chf": best["old_price"],
                "change_pct": best["change_pct"],
                "period_days": best["period_days"],
                "listings_count": best["sample_size"],
                "sparkline": best["sparkline"],
            }

        # ── most_offered (highest active listings = most supply on market) ────
        appreciated_ref = most_appreciated.get("reference", "")

        offered_candidates = [
            c for c in appreciation_candidates
            if c["reference"] != appreciated_ref and c["sample_size"] > 0
        ]

        if not offered_candidates:
            most_offered = _empty_offered_card()
        else:
            top = max(offered_candidates, key=lambda x: x["sample_size"])
            brand_o, model_o = _lookup_brand_model(top["reference"], ar_cur)
            count_o = top["sample_size"]

            if count_o >= 200:
                note_it = f"{count_o} annunci attivi — offerta molto abbondante. Alta concorrenza tra i venditori."
                note_en = f"{count_o} active listings — very abundant supply. High seller competition."
            elif count_o >= 80:
                note_it = f"{count_o} annunci attivi — mercato liquido con buona disponibilità."
                note_en = f"{count_o} active listings — liquid market with good availability."
            else:
                note_it = f"{count_o} annunci attivi nel mercato secondario globale."
                note_en = f"{count_o} active listings in the global secondary market."

            most_offered = {
                "has_data": True,
                "reference": top["reference"],
                "brand": brand_o,
                "model": model_o,
                "listings_count": count_o,
                "current_price_chf": top["new_price"],
                "change_pct_6m": top["change_pct"],
                "supply_note": note_it,
                "supply_note_en": note_en,
            }

        # ── rarest (fewest active listings, different from most_appreciated & most_offered) ─
        offered_ref = most_offered.get("reference", "")

        # exclude refs already shown in other cards
        rarest_candidates = [
            c for c in appreciation_candidates
            if c["reference"] not in (appreciated_ref, offered_ref)
            and c["sample_size"] > 0
        ]

        if not rarest_candidates:
            # If all refs are already used, allow any ref not in appreciated
            rarest_candidates = [
                c for c in appreciation_candidates
                if c["reference"] != appreciated_ref and c["sample_size"] > 0
            ]

        if not rarest_candidates:
            rarest = _empty_rarest_card()
        else:
            rarest_cand = min(rarest_candidates, key=lambda x: x["sample_size"])
            brand_r, model_r = _lookup_brand_model(rarest_cand["reference"], ar_cur)

            # compute 6m change for rarest
            change_6m = None
            for cand in appreciation_candidates:
                if cand["reference"] == rarest_cand["reference"]:
                    change_6m = cand["change_pct"]
                    break

            scarcity_count = rarest_cand["sample_size"]
            if scarcity_count <= 5:
                note_it = f"Solo {scarcity_count} annunci attivi nel mercato secondario globale. Disponibilità estremamente limitata."
                note_en = f"Only {scarcity_count} active listings in the global secondary market. Extremely limited availability."
            elif scarcity_count <= 20:
                note_it = f"{scarcity_count} annunci attivi — offerta scarsa, domanda sostenuta dai collezionisti."
                note_en = f"{scarcity_count} active listings — tight supply, sustained collector demand."
            else:
                note_it = f"{scarcity_count} annunci attivi — tra i modelli meno offerti nel mercato secondario."
                note_en = f"{scarcity_count} active listings — among the least offered models on the secondary market."

            rarest = {
                "has_data": True,
                "reference": rarest_cand["reference"],
                "brand": brand_r,
                "model": model_r,
                "listings_count": scarcity_count,
                "current_price_chf": rarest_cand["new_price"],
                "change_pct_6m": change_6m,
                "scarcity_note": note_it,  # default IT; frontend can pick by lang
                "scarcity_note_en": note_en,
            }

    finally:
        ph.close()
        ar.close()

    return {
        "most_appreciated": most_appreciated,
        "most_offered": most_offered,
        "rarest": rarest,
        "computed_at": now.isoformat(),
    }


# ── Empty fallbacks ────────────────────────────────────────────────────────────

def _empty_appreciation_card() -> dict:
    return {
        "has_data": False,
        "reference": "—",
        "brand": "—",
        "model": "Dati non disponibili",
        "current_price_chf": 0,
        "price_6m_ago_chf": 0,
        "change_pct": 0.0,
        "period_days": 180,
        "listings_count": 0,
        "sparkline": [],
    }


def _empty_offered_card() -> dict:
    return {
        "has_data": False,
        "reference": "—",
        "brand": "—",
        "model": "Dati non disponibili",
        "listings_count": 0,
        "current_price_chf": 0,
        "change_pct_6m": None,
        "supply_note": "Dati in aggiornamento.",
        "supply_note_en": "Data updating.",
    }


def _empty_rarest_card() -> dict:
    return {
        "has_data": False,
        "reference": "—",
        "brand": "—",
        "model": "Dati non disponibili",
        "listings_count": 0,
        "current_price_chf": 0,
        "change_pct_6m": None,
        "scarcity_note": "Dati in aggiornamento.",
        "scarcity_note_en": "Data updating.",
    }
