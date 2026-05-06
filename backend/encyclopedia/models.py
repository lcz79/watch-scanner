from pydantic import BaseModel


class WatchData(BaseModel):
    brand: str
    model: str
    reference: str
    collection: str | None = None
    year_introduced: int | None = None
    year_discontinued: int | None = None
    case_material: str | None = None
    case_diameter_mm: float | None = None
    case_thickness_mm: float | None = None
    water_resistance_m: int | None = None
    movement_type: str | None = None
    movement_caliber: str | None = None
    power_reserve_h: int | None = None
    frequency_vph: int | None = None
    jewels: int | None = None
    dial_color: str | None = None
    dial_material: str | None = None
    bracelet_type: str | None = None
    clasp_type: str | None = None
    retail_price_eur: float | None = None
    avg_market_price_eur: float | None = None
    description: str | None = None
    technical_notes: str | None = None
    is_discontinued: bool = False
    is_limited_edition: bool = False
    production_numbers: int | None = None
    images: list[str] = []
    variants: list[str] = []
    stories: list[dict] = []


class WatchVariant(BaseModel):
    parent_reference: str
    variant_reference: str
    description: str | None = None


class WatchStory(BaseModel):
    reference: str
    category: str | None = None  # "history", "celebrity", "auction_record", "technical"
    title: str
    content: str
    source_url: str | None = None


class WatchImage(BaseModel):
    reference: str
    url: str
    source: str | None = None   # "official", "chrono24", "marketplace"
    is_primary: bool = False
    local_path: str | None = None


class EncyclopediaSearchResult(BaseModel):
    reference: str
    brand: str
    model: str
    collection: str | None = None
    case_material: str | None = None
    dial_color: str | None = None
    retail_price_eur: float | None = None
    avg_market_price_eur: float | None = None
    description: str | None = None
    is_discontinued: bool = False
