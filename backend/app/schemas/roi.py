from pydantic import BaseModel, Field
from typing import Optional


class ROIInput(BaseModel):
    selling_price: float = Field(..., gt=0, description="Current selling price (MYR)")
    cost_price: float = Field(..., gt=0, description="Cost/COGS per unit (MYR)")
    monthly_units: float = Field(..., gt=0, description="Current monthly units sold")
    price_elasticity: float = Field(default=-1.5, description="Price elasticity of demand (negative)")
    market_median_price: Optional[float] = Field(None, description="Market median from Fair Price Engine")


class PriceScenario(BaseModel):
    price: float
    units: float
    revenue: float
    gross_profit: float
    margin_pct: float
    vs_current_revenue_pct: float
    vs_current_profit_pct: float


class ROIOutput(BaseModel):
    current: PriceScenario
    break_even_price: float
    break_even_units: float
    optimal_price: float
    optimal_revenue: float
    optimal_margin_pct: float
    scenarios: list[PriceScenario]
    recommendation: str
    market_position: Optional[str] = None
