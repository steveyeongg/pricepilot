import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.price import PriceSnapshot
from app.models.product import TrackedProduct
from app.schemas.analytics import FairPriceAnalysis, MarketPosition, PriceHistory, PricePoint
from app.services.fair_price_engine import get_fair_price_analysis, get_market_position

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/products/{product_id}/fair-price", response_model=FairPriceAnalysis)
async def product_fair_price(
    product_id: uuid.UUID,
    lookback_hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_fair_price_analysis(db, product_id, lookback_hours)
    if not analysis:
        raise HTTPException(status_code=404, detail="Not enough price data for this product")
    return analysis


@router.get("/products/{product_id}/position", response_model=MarketPosition)
async def product_market_position(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    product = await db.get(TrackedProduct, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.user_price:
        raise HTTPException(status_code=422, detail="Product has no user_price set")

    analysis = await get_fair_price_analysis(db, product_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Not enough price data")

    # Build per-platform summary
    result = await db.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.product_id == product_id)
        .order_by(PriceSnapshot.captured_at.desc())
        .limit(200)
    )
    snapshots = result.scalars().all()
    platform_map: dict[str, list[float]] = {}
    for s in snapshots:
        platform_map.setdefault(s.platform, []).append(float(s.price))

    platform_breakdown = [
        {"platform": plat, "min": min(prices), "max": max(prices), "avg": round(sum(prices) / len(prices), 2)}
        for plat, prices in platform_map.items()
    ]

    return get_market_position(float(product.user_price), analysis, platform_breakdown)


@router.get("/products/{product_id}/history", response_model=PriceHistory)
async def product_price_history(
    product_id: uuid.UUID,
    platform: str | None = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    filters = [
        PriceSnapshot.product_id == product_id,
        PriceSnapshot.captured_at >= cutoff,
    ]
    if platform:
        filters.append(PriceSnapshot.platform == platform)

    result = await db.execute(
        select(PriceSnapshot)
        .where(and_(*filters))
        .order_by(PriceSnapshot.captured_at.asc())
    )
    snapshots = result.scalars().all()

    return PriceHistory(
        product_id=str(product_id),
        platform=platform,
        data_points=[
            PricePoint(
                platform=s.platform,
                price=float(s.price),
                captured_at=s.captured_at,
                url=s.url,
            )
            for s in snapshots
        ],
    )


@router.get("/dashboard")
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Aggregate stats for the dashboard home page."""
    products = (await db.execute(select(TrackedProduct))).scalars().all()
    total_products = len(products)

    cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    recent = (await db.execute(
        select(PriceSnapshot).where(PriceSnapshot.captured_at >= cutoff_24h)
    )).scalars().all()

    platforms = list({s.platform for s in recent})
    avg_price = round(sum(float(s.price) for s in recent) / len(recent), 2) if recent else 0

    return {
        "total_products_tracked": total_products,
        "price_checks_last_24h": len(recent),
        "platforms_active": len(platforms),
        "avg_tracked_price_myr": avg_price,
    }
