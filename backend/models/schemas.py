from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class WatchQuery(BaseModel):
    reference: str = Field(..., description="Referenza orologio es. '116610LN', '5711/1A'")
    brand: str | None = None
    max_price: float | None = None
    currency: str = "EUR"


class WatchListing(BaseModel):
    source: str
    reference: str
    price: float
    currency: str = "EUR"
    seller: str
    url: str
    condition: Literal["new", "mint", "good", "fair", "unknown"] = "unknown"
    scraped_at: datetime
    image_url: str | None = None
    location: str | None = None
    description: str | None = None


class ScanResult(BaseModel):
    scan_id: str
    query: WatchQuery
    listings: list[WatchListing]
    best_price: float | None = None
    best_listing: WatchListing | None = None
    total_found: int
    scanned_at: datetime
    agents_used: list[str]
    duration_seconds: float


class AgentStatus(BaseModel):
    name: str
    status: Literal["ok", "error", "mock"]
    mock_mode: bool
    last_run: datetime | None = None
    error: str | None = None


class AlertConfig(BaseModel):
    reference: str
    brand: str | None = None
    max_price: float
    currency: str = "EUR"
    notify_email: str | None = None       # indirizzo email destinatario
    notify_whatsapp: str | None = None    # numero WhatsApp es. +393331234567
    notify_telegram_chat_id: str | None = None  # Telegram chat ID per questo alert


class Alert(BaseModel):
    alert_id: str
    config: AlertConfig
    created_at: datetime
    active: bool = True
    last_triggered: datetime | None = None
