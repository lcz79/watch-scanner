"""Market Price Engine — calcola True Market Price da una lista di listings."""
import math
import statistics
from models.schemas import WatchListing


def remove_outliers_iqr(prices: list[float]) -> list[float]:
    """Rimuove outlier con metodo IQR."""
    if len(prices) < 4:
        return prices
    sorted_p = sorted(prices)
    q1 = sorted_p[len(sorted_p) // 4]
    q3 = sorted_p[3 * len(sorted_p) // 4]
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [p for p in prices if lo <= p <= hi]


def _percentile(sorted_data: list[float], p: float) -> float:
    """Calcola il percentile p (0-100) da una lista già ordinata."""
    if not sorted_data:
        return 0.0
    if len(sorted_data) == 1:
        return sorted_data[0]
    idx = (p / 100) * (len(sorted_data) - 1)
    lower = int(idx)
    upper = lower + 1
    if upper >= len(sorted_data):
        return sorted_data[-1]
    frac = idx - lower
    return sorted_data[lower] + frac * (sorted_data[upper] - sorted_data[lower])


def compute_market_stats(listings: list[WatchListing]) -> dict:
    """
    Ritorna:
    {
        "min_price", "max_price", "median_price", "mean_price",
        "p25", "p75", "fair_price", "sample_size", "outliers_removed"
    }
    """
    if not listings:
        return {
            "min_price": None,
            "max_price": None,
            "median_price": None,
            "mean_price": None,
            "p25": None,
            "p75": None,
            "fair_price": None,
            "sample_size": 0,
            "outliers_removed": 0,
        }

    all_prices = [l.price for l in listings]
    cleaned_prices = remove_outliers_iqr(all_prices)
    outliers_removed = len(all_prices) - len(cleaned_prices)

    if not cleaned_prices:
        cleaned_prices = all_prices

    sorted_p = sorted(cleaned_prices)

    min_price = sorted_p[0]
    max_price = sorted_p[-1]
    median_price = statistics.median(sorted_p)
    mean_price = statistics.mean(sorted_p)
    p25 = _percentile(sorted_p, 25)
    p75 = _percentile(sorted_p, 75)
    # Fair price: media ponderata tra mediana (60%) e media (40%)
    fair_price = median_price * 0.6 + mean_price * 0.4

    return {
        "min_price": min_price,
        "max_price": max_price,
        "median_price": median_price,
        "mean_price": mean_price,
        "p25": p25,
        "p75": p75,
        "fair_price": fair_price,
        "sample_size": len(cleaned_prices),
        "outliers_removed": outliers_removed,
    }


def compute_price_distribution(listings: list[WatchListing], bins: int = 10) -> dict:
    """
    Ritorna:
    {
        "bins": [{"range": "27000-28000", "count": 5, "percentage": 12.5}, ...],
        "percentile_bands": {"p10": x, "p25": x, "p50": x, "p75": x, "p90": x}
    }
    """
    if not listings:
        return {
            "bins": [],
            "percentile_bands": {"p10": None, "p25": None, "p50": None, "p75": None, "p90": None},
        }

    prices = [l.price for l in listings]
    sorted_p = sorted(prices)
    min_p = sorted_p[0]
    max_p = sorted_p[-1]

    percentile_bands = {
        "p10": _percentile(sorted_p, 10),
        "p25": _percentile(sorted_p, 25),
        "p50": _percentile(sorted_p, 50),
        "p75": _percentile(sorted_p, 75),
        "p90": _percentile(sorted_p, 90),
    }

    if min_p == max_p:
        return {
            "bins": [{"range": f"{int(min_p)}-{int(max_p)}", "count": len(prices), "percentage": 100.0}],
            "percentile_bands": percentile_bands,
        }

    bin_width = (max_p - min_p) / bins
    bin_counts = [0] * bins

    for price in prices:
        idx = int((price - min_p) / bin_width)
        if idx >= bins:
            idx = bins - 1
        bin_counts[idx] += 1

    total = len(prices)
    bin_list = []
    for i in range(bins):
        lo = min_p + i * bin_width
        hi = min_p + (i + 1) * bin_width
        count = bin_counts[i]
        if count > 0 or i < bins - 1:
            bin_list.append({
                "range": f"{int(lo)}-{int(hi)}",
                "count": count,
                "percentage": round(count / total * 100, 1),
            })

    return {
        "bins": bin_list,
        "percentile_bands": percentile_bands,
    }
