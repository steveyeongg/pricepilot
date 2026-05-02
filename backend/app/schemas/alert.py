import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal


class AlertCreate(BaseModel):
    product_id: uuid.UUID
    alert_type: Literal["price_drop", "price_spike", "competitor_change", "back_in_stock", "target_price"]
    threshold_pct: Optional[float] = Field(None, ge=0, le=100)
    threshold_price: Optional[float] = Field(None, ge=0)
    direction: Optional[Literal["above", "below"]] = None
    platform_filter: Optional[str] = None


class AlertOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    product_id: uuid.UUID
    alert_type: str
    threshold_pct: Optional[float]
    threshold_price: Optional[float]
    direction: Optional[str]
    platform_filter: Optional[str]
    is_active: bool
    last_triggered: Optional[datetime]
    created_at: datetime


class AlertEventOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    alert_id: uuid.UUID
    message: str
    old_price: Optional[float]
    new_price: Optional[float]
    platform: Optional[str]
    fired_at: datetime
