import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    brand: Optional[str] = None
    category: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    search_query: Optional[str] = None
    user_price: Optional[float] = Field(None, ge=0)
    user_cost: Optional[float] = Field(None, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    brand: Optional[str] = None
    category: Optional[str] = None
    user_price: Optional[float] = Field(None, ge=0)
    user_cost: Optional[float] = Field(None, ge=0)


class ProductOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    brand: Optional[str]
    category: Optional[str]
    barcode: Optional[str]
    image_url: Optional[str]
    search_query: Optional[str]
    user_price: Optional[float]
    user_cost: Optional[float]
    created_at: datetime
    updated_at: datetime
