from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PricePoint(BaseModel):
    platform: str
    price: float
    captured_at: datetime
    url: Optional[str]


class PriceHistory(BaseModel):
    product_id: str
    platform: Optional[str]
    data_points: list[PricePoint]


class FairPriceAnalysis(BaseModel):
    product_id: str
    product_name: str

    # Core stats
    min_price: float
    max_price: float
    mean_price: float
    median_price: float
    std_dev: float

    # Fair price range (median ± 1 std dev)
    fair_price_low: float
    fair_price_high: float

    # Classification thresholds
    cheap_threshold: float    # below 25th percentile
    expensive_threshold: float  # above 75th percentile

    total_listings: int
    platforms_covered: list[str]
    last_updated: datetime


class MarketPosition(BaseModel):
    user_price: float
    market_median: float
    percentile: float  # 0–100
    classification: str  # Cheap / Fair / Expensive
    vs_median_pct: float  # +/- % vs market median
    recommendation: str
    platform_breakdown: list[dict]
