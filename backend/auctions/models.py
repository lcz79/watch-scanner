"""
Pydantic models per il sistema aste.
"""
from pydantic import BaseModel, Field
from typing import Optional


class AuctionResult(BaseModel):
    id: Optional[int] = None
    auction_house: str
    sale_name: Optional[str] = None
    sale_location: Optional[str] = None
    sale_date: str
    lot_number: Optional[str] = None
    brand: str
    model: str
    reference: Optional[str] = None
    description: Optional[str] = None
    year_made: Optional[str] = None
    condition: Optional[str] = None
    estimate_low_chf: Optional[float] = None
    estimate_high_chf: Optional[float] = None
    hammer_price_chf: Optional[float] = None
    buyer_premium_pct: float = 26.0
    total_price_chf: Optional[float] = None
    currency: str = "CHF"
    lot_url: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None
    is_record: bool = False
    created_at: Optional[str] = None

    # Campi calcolati che possono essere aggiunti nelle risposte API
    hammer_to_estimate_ratio: Optional[float] = None
    estimate_midpoint_chf: Optional[float] = None


class AuctionSentiment(BaseModel):
    reference: str
    brand: str
    calculation_date: str
    total_lots: Optional[int] = None
    avg_hammer_to_estimate_ratio: Optional[float] = None
    sell_through_rate: Optional[float] = None
    price_trend_12m: Optional[float] = None
    price_trend_36m: Optional[float] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None


class UpcomingAuction(BaseModel):
    house: str
    sale_name: str
    location: str
    date: str
    preview_date: Optional[str] = None
    url: Optional[str] = None
    focus: Optional[str] = None
    highlights: Optional[list[str]] = None


class AuctionHouseStats(BaseModel):
    auction_house: str
    total_lots: int
    first_sale: Optional[str] = None
    last_sale: Optional[str] = None
    avg_hammer_chf: Optional[float] = None
    max_hammer_chf: Optional[float] = None
    total_sales: Optional[int] = None
