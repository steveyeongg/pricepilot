import time
from fastapi import APIRouter, Query
from typing import Optional

from app.scrapers import search_all, ALL_PLATFORMS
from app.schemas.price import SearchResult, PlatformResult
from app.services.fair_price_engine import compute_fair_price_from_results
from app.schemas.analytics import FairPriceAnalysis

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResult)
async def search_prices(
    q: str = Query(..., min_length=1, description="Product search query"),
    platforms: Optional[str] = Query(None, description="Comma-separated platform names"),
    limit: int = Query(10, ge=1, le=30, description="Results per platform"),
):
    """Search prices across all supported Malaysian platforms in real-time."""
    platform_list = [p.strip() for p in platforms.split(",")] if platforms else None

    start = time.monotonic()
    raw = await search_all(q, platforms=platform_list, limit_per_platform=limit)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    results = [
        PlatformResult(
            platform=r["platform"],
            seller_name=r.get("seller_name"),
            price=r["price"],
            original_price=r.get("original_price"),
            discount_pct=r.get("discount_pct"),
            currency=r.get("currency", "MYR"),
            url=r.get("url"),
            in_stock=r.get("in_stock", True),
            rating=r.get("rating"),
            review_count=r.get("review_count"),
            image_url=r.get("image_url"),
            title=r.get("title", q),
        )
        for r in raw
        if r.get("price") and float(r["price"]) > 0
    ]

    results.sort(key=lambda x: x.price)

    queried = list({r.platform for r in results})

    return SearchResult(
        query=q,
        total_results=len(results),
        results=results,
        platforms_queried=queried,
        search_duration_ms=elapsed_ms,
    )


@router.get("/fair-price", response_model=FairPriceAnalysis)
async def get_fair_price(
    q: str = Query(..., min_length=1),
    platforms: Optional[str] = Query(None),
):
    """Search + compute fair price in one shot (no DB required)."""
    platform_list = [p.strip() for p in platforms.split(",")] if platforms else None
    raw = await search_all(q, platforms=platform_list, limit_per_platform=15)
    valid = [r for r in raw if r.get("price") and float(r["price"]) > 0]
    if not valid:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No results found for this query")
    return compute_fair_price_from_results("live", q, valid)


@router.get("/platforms")
async def list_platforms():
    return {"platforms": ALL_PLATFORMS}
