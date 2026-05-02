import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class PriceSnapshotOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    product_id: uuid.UUID
    platform: str
    seller_name: Optional[str]
    price: float
    original_price: Optional[float]
    discount_pct: Optional[float]
    currency: str
    url: Optional[str]
    in_stock: bool
    rating: Optional[float]
    review_count: Optional[int]
    captured_at: datetime


class PlatformResult(BaseModel):
    platform: str
    seller_name: Optional[str]
    price: float
    original_price: Optional[float]
    discount_pct: Optional[float]
    currency: str = "MYR"
    url: Optional[str]
    in_stock: bool = True
    rating: Optional[float]
    review_count: Optional[int]
    image_url: Optional[str]
    title: str


class SearchResult(BaseModel):
    query: str
    total_results: int
    results: list[PlatformResult]
    platforms_queried: list[str]
    search_duration_ms: int
