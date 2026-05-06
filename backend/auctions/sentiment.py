"""
Sentiment engine per le aste di orologi di lusso.
Analizza i risultati storici e produce un punteggio di sentiment per referenza.
"""
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger("auctions")

# Soglie per il sentiment score
SCORE_THRESHOLDS = {
    "Strong Buy": 75,
    "Accumulate": 55,
    "Hold": 35,
    "Reduce": 15,
    "Sell": 0,
}


def _label_from_score(score: float) -> str:
    if score >= 75:
        return "Strong Buy"
    elif score >= 55:
        return "Accumulate"
    elif score >= 35:
        return "Hold"
    elif score >= 15:
        return "Reduce"
    else:
        return "Sell"


def _parse_date(date_str: str) -> datetime | None:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def compute_sentiment(reference: str, results: list[dict]) -> dict:
    """
    Analizza i risultati d'asta per una referenza e produce un sentiment score.

    Logica di scoring (totale 100 punti):
    - Sell-through rate (quanti lotti venduti vs totali passati): 0-25 pt
    - Hammer vs estimate medio (sopra o sotto stima): 0-25 pt
    - Trend prezzi ultimi 12 mesi: 0-20 pt
    - Ultimi 3 lotti tutti sopra stima: bonus 15 pt
    - Frequenza aste recenti (momentum): 0-15 pt

    Ritorna:
    {
        "score": 0-100,
        "label": "Strong Buy" | "Accumulate" | "Hold" | "Reduce" | "Sell",
        "sell_through_rate": float,
        "avg_premium_over_estimate": float,
        "price_trend_12m": float,
        "price_trend_36m": float,
        "total_auction_records": int,
        "last_sale_date": str | None,
        "last_hammer_price_chf": float | None,
        "notes": str
    }
    """
    if not results:
        return {
            "score": 0.0,
            "label": "Sell",
            "sell_through_rate": 0.0,
            "avg_premium_over_estimate": 0.0,
            "price_trend_12m": 0.0,
            "price_trend_36m": 0.0,
            "total_auction_records": 0,
            "last_sale_date": None,
            "last_hammer_price_chf": None,
            "notes": "Nessun dato d'asta disponibile per questa referenza.",
        }

    now = datetime.utcnow()
    cutoff_12m = now - timedelta(days=365)
    cutoff_36m = now - timedelta(days=3 * 365)

    # Filtra risultati con hammer price (lotti venduti)
    sold = [r for r in results if r.get("hammer_price_chf") and r["hammer_price_chf"] > 0]
    total_lots = len(results)
    sold_lots = len(sold)

    # -------------------------------------------------------------------------
    # 1) Sell-through rate (0-25 punti)
    # -------------------------------------------------------------------------
    sell_through = sold_lots / total_lots if total_lots > 0 else 0.0
    stt_score = sell_through * 25  # 100% → 25 pt

    # -------------------------------------------------------------------------
    # 2) Hammer vs estimate ratio (0-25 punti)
    # -------------------------------------------------------------------------
    ratios = []
    for r in sold:
        low = r.get("estimate_low_chf")
        high = r.get("estimate_high_chf")
        hammer = r.get("hammer_price_chf")
        if low and high and hammer and (low + high) > 0:
            mid = (low + high) / 2.0
            ratios.append(hammer / mid)

    avg_ratio = sum(ratios) / len(ratios) if ratios else 1.0
    # ratio 1.0 = in stima → 12.5 pt; 1.5 = +50% stima → 25 pt; 0.5 = -50% → 0 pt
    ratio_score = max(0.0, min(25.0, (avg_ratio - 0.5) * 25.0))
    avg_premium_pct = (avg_ratio - 1.0) if ratios else 0.0

    # -------------------------------------------------------------------------
    # 3) Trend prezzi 12 mesi (0-20 punti)
    # -------------------------------------------------------------------------
    sold_with_dates = [
        r for r in sold
        if _parse_date(r.get("sale_date"))
    ]
    sold_with_dates.sort(key=lambda r: r["sale_date"])

    recent_12m = [
        r for r in sold_with_dates
        if _parse_date(r["sale_date"]) and _parse_date(r["sale_date"]) >= cutoff_12m
    ]
    older_12m_36m = [
        r for r in sold_with_dates
        if _parse_date(r["sale_date"]) and cutoff_36m <= _parse_date(r["sale_date"]) < cutoff_12m
    ]

    price_trend_12m = 0.0
    if recent_12m and older_12m_36m:
        avg_recent = sum(r["hammer_price_chf"] for r in recent_12m) / len(recent_12m)
        avg_older = sum(r["hammer_price_chf"] for r in older_12m_36m) / len(older_12m_36m)
        if avg_older > 0:
            price_trend_12m = (avg_recent - avg_older) / avg_older

    # Trend score: +20% → 20 pt; 0% → 10 pt; -20% → 0 pt
    trend_score_12m = max(0.0, min(20.0, (price_trend_12m + 0.2) * 50.0))

    # Trend 36 mesi
    price_trend_36m = 0.0
    very_old = [
        r for r in sold_with_dates
        if _parse_date(r["sale_date"]) and _parse_date(r["sale_date"]) < cutoff_36m
    ]
    if recent_12m and very_old:
        avg_recent = sum(r["hammer_price_chf"] for r in recent_12m) / len(recent_12m)
        avg_very_old = sum(r["hammer_price_chf"] for r in very_old) / len(very_old)
        if avg_very_old > 0:
            price_trend_36m = (avg_recent - avg_very_old) / avg_very_old

    # -------------------------------------------------------------------------
    # 4) Bonus: ultimi 3 lotti tutti sopra stima (+0-15 punti)
    # -------------------------------------------------------------------------
    last_3 = sold_with_dates[-3:] if len(sold_with_dates) >= 3 else sold_with_dates
    above_count = 0
    for r in last_3:
        low = r.get("estimate_low_chf")
        high = r.get("estimate_high_chf")
        hammer = r.get("hammer_price_chf")
        if low and high and hammer:
            if hammer > high:
                above_count += 1
    if len(last_3) > 0:
        bonus_above = (above_count / len(last_3)) * 15.0
    else:
        bonus_above = 0.0

    # -------------------------------------------------------------------------
    # 5) Frequenza aste recenti / momentum (0-15 punti)
    # -------------------------------------------------------------------------
    cutoff_6m = now - timedelta(days=183)
    lots_6m = len([r for r in sold_with_dates if _parse_date(r["sale_date"]) and _parse_date(r["sale_date"]) >= cutoff_6m])
    # 3+ lotti negli ultimi 6 mesi = punteggio pieno
    momentum_score = min(15.0, lots_6m * 5.0)

    # -------------------------------------------------------------------------
    # Calcolo score finale
    # -------------------------------------------------------------------------
    raw_score = stt_score + ratio_score + trend_score_12m + bonus_above + momentum_score
    score = round(min(100.0, max(0.0, raw_score)), 1)
    label = _label_from_score(score)

    # Last sale info
    last_sale_date = sold_with_dates[-1]["sale_date"] if sold_with_dates else None
    last_hammer = sold_with_dates[-1]["hammer_price_chf"] if sold_with_dates else None

    # Note narrative
    notes_parts = []
    if sell_through > 0.9:
        notes_parts.append(f"Sell-through rate elevato ({sell_through:.0%})")
    elif sell_through < 0.6:
        notes_parts.append(f"Sell-through rate basso ({sell_through:.0%})")

    if avg_premium_pct > 0.15:
        notes_parts.append(f"Supera sistematicamente la stima (+{avg_premium_pct:.0%} in media)")
    elif avg_premium_pct < -0.1:
        notes_parts.append(f"Tende a vendere sotto stima ({avg_premium_pct:.0%} in media)")

    if price_trend_12m > 0.1:
        notes_parts.append(f"Trend prezzi positivo +{price_trend_12m:.0%} ultimi 12 mesi")
    elif price_trend_12m < -0.1:
        notes_parts.append(f"Trend prezzi negativo {price_trend_12m:.0%} ultimi 12 mesi")

    if above_count == len(last_3) and len(last_3) == 3:
        notes_parts.append("Ultimi 3 lotti tutti sopra stima massima")

    notes = " | ".join(notes_parts) if notes_parts else "Dati insufficienti per analisi approfondita"

    logger.debug(
        f"Sentiment {reference}: score={score} label={label} "
        f"stt={sell_through:.2f} ratio={avg_ratio:.2f} trend12m={price_trend_12m:.2f}"
    )

    return {
        "score": score,
        "label": label,
        "sell_through_rate": round(sell_through, 4),
        "avg_premium_over_estimate": round(avg_premium_pct, 4),
        "price_trend_12m": round(price_trend_12m, 4),
        "price_trend_36m": round(price_trend_36m, 4),
        "total_auction_records": total_lots,
        "last_sale_date": last_sale_date,
        "last_hammer_price_chf": last_hammer,
        "notes": notes,
    }


def enrich_results(results: list[dict]) -> list[dict]:
    """
    Aggiunge campi calcolati a ogni risultato:
    - hammer_to_estimate_ratio
    - estimate_midpoint_chf
    - performance_label
    """
    enriched = []
    for r in results:
        r = dict(r)
        low = r.get("estimate_low_chf")
        high = r.get("estimate_high_chf")
        hammer = r.get("hammer_price_chf")

        if low and high:
            r["estimate_midpoint_chf"] = (low + high) / 2.0
        else:
            r["estimate_midpoint_chf"] = None

        if hammer and low and high and (low + high) > 0:
            mid = (low + high) / 2.0
            ratio = hammer / mid
            r["hammer_to_estimate_ratio"] = round(ratio, 3)
            if hammer > high * 1.5:
                r["performance_label"] = "Record"
            elif hammer > high:
                r["performance_label"] = "Sopra stima"
            elif hammer >= low:
                r["performance_label"] = "In stima"
            else:
                r["performance_label"] = "Sotto stima"
        else:
            r["hammer_to_estimate_ratio"] = None
            r["performance_label"] = "N/D"

        enriched.append(r)
    return enriched
