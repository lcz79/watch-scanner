"""Calcola investment score (0-100) per una referenza."""
from analytics.price_history import compute_trend


def compute_investment_score(reference: str, market_stats: dict, listings_count: int) -> dict:
    """
    Ritorna:
    {
        "investment_score": 0-100,
        "trend": "up"/"down"/"stable",
        "volatility": float,
        "liquidity": "high"/"medium"/"low",
        "signal": "buy"/"hold"/"avoid"
    }
    Logic:
    - trend up → +30 punti
    - bassa volatilità → +20
    - listings_count > 10 → liquidità alta → +20
    - price < historical_median * 0.95 → +30 (buying opportunity)
    """
    trend_data = compute_trend(reference)
    trend = trend_data["trend"]
    volatility = trend_data["volatility"]
    change_30d = trend_data.get("change_30d", 0.0)

    score = 0.0

    # 1. Trend score: +30 se up, +10 se stable, 0 se down
    if trend == "up":
        score += 30
    elif trend == "stable":
        score += 10
    # down → 0

    # 2. Volatilità: +20 se bassa (< 5%), scala lineare fino a 0 se >= 20%
    if volatility < 0.05:
        score += 20
    elif volatility < 0.20:
        score += 20 * (1 - (volatility - 0.05) / 0.15)
    # else: 0

    # 3. Liquidità: listings_count
    if listings_count > 10:
        liquidity = "high"
        score += 20
    elif listings_count >= 5:
        liquidity = "medium"
        score += 10
    else:
        liquidity = "low"
        score += 0

    # 4. Buying opportunity: current market price vs historical median
    current_median = market_stats.get("median_price")
    # Usa il trend 30d per stimare la distanza dal prezzo storico
    # Se i prezzi sono scesi di > 5% negli ultimi 30gg → opportunità
    if change_30d < -0.05:
        score += 30
    elif change_30d < 0:
        # Proporzionale tra 0 e 30
        score += 30 * abs(change_30d) / 0.05
    # Se non abbiamo dati storici ma fair_price è disponibile, nessun bonus

    score = max(0.0, min(100.0, score))

    # Signal
    if score >= 65:
        signal = "buy"
    elif score >= 35:
        signal = "hold"
    else:
        signal = "avoid"

    return {
        "investment_score": round(score, 1),
        "trend": trend,
        "volatility": volatility,
        "liquidity": liquidity,
        "signal": signal,
    }
