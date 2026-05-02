"""
Fair Price Intelligence Engine.
Computes fair price ranges, market stats, and seller positioning from price snapshots.
"""
import statistics
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price import PriceSnapshot
from app.models.product import TrackedProduct
from app.schemas.analytics import FairPriceAnalysis, MarketPosition


async def get_fair_price_analysis(
    db: AsyncSession,
    product_id: uuid.UUID,
    lookback_hours: int = 24,
) -> Optional[FairPriceAnalysis]:
    """Compute fair price stats from recent snapshots for a tracked product."""
    cutoff = datetime.now(timezone.utc).replace(
        hour=datetime.now(timezone.utc).hour - lookback_hours
    )

    result = await db.execute(
        select(PriceSnapshot, TrackedProduct)
        .join(TrackedProduct)
        .where(
            and_(
                PriceSnapshot.product_id == product_id,
                PriceSnapshot.in_stock == True,
            )
        )
        .order_by(PriceSnapshot.captured_at.desc())
    )
    rows = result.all()

    if not rows:
        return None

    product = rows[0][1]
    prices = [float(row[0].price) for row in rows]
    platforms = list({row[0].platform for row in rows})

    return _compute_analysis(str(product_id), product.name, prices, platforms)


def compute_fair_price_from_results(
    product_id: str,
    product_name: str,
    results: list[dict],
) -> FairPriceAnalysis:
    """Compute fair price analysis from raw scrape results (no DB needed)."""
    prices = [float(r["price"]) for r in results if r.get("price") and float(r["price"]) > 0]
    platforms = list({r.get("platform", "unknown") for r in results})
    return _compute_analysis(product_id, product_name, prices, platforms)


def _compute_analysis(
    product_id: str,
    product_name: str,
    prices: list[float],
    platforms: list[str],
) -> FairPriceAnalysis:
    if not prices:
        raise ValueError("No prices to analyse")

    sorted_prices = sorted(prices)
    n = len(sorted_prices)

    mean = statistics.mean(prices)
    median = statistics.median(prices)
    std = statistics.stdev(prices) if n > 1 else 0.0

    def percentile(p: float) -> float:
        idx = (p / 100) * (n - 1)
        lo, hi = int(idx), min(int(idx) + 1, n - 1)
        return sorted_prices[lo] + (sorted_prices[hi] - sorted_prices[lo]) * (idx - lo)

    return FairPriceAnalysis(
        product_id=product_id,
        product_name=product_name,
        min_price=sorted_prices[0],
        max_price=sorted_prices[-1],
        mean_price=round(mean, 2),
        median_price=round(median, 2),
        std_dev=round(std, 2),
        fair_price_low=round(max(median - std, sorted_prices[0]), 2),
        fair_price_high=round(min(median + std, sorted_prices[-1]), 2),
        cheap_threshold=round(percentile(25), 2),
        expensive_threshold=round(percentile(75), 2),
        total_listings=n,
        platforms_covered=platforms,
        last_updated=datetime.now(timezone.utc),
    )


def get_market_position(
    user_price: float,
    analysis: FairPriceAnalysis,
    platform_prices: list[dict] | None = None,
) -> MarketPosition:
    """Classify a seller's price vs the market and generate a recommendation."""
    prices = _reconstruct_sorted_prices(analysis)
    n = len(prices)

    # Compute percentile of user_price within the distribution
    rank = sum(1 for p in prices if p <= user_price)
    percentile = (rank / n) * 100 if n else 50.0

    vs_median = ((user_price - analysis.median_price) / analysis.median_price) * 100

    if user_price <= analysis.cheap_threshold:
        classification = "Cheap"
        recommendation = (
            f"Your price is in the bottom 25% of the market. "
            f"Consider raising to MYR {analysis.fair_price_low:.2f}–{analysis.fair_price_high:.2f} "
            f"to improve margins without losing competitiveness."
        )
    elif user_price >= analysis.expensive_threshold:
        classification = "Expensive"
        recommendation = (
            f"Your price is above the 75th percentile. "
            f"You risk losing buyers to competitors. "
            f"Consider pricing closer to MYR {analysis.median_price:.2f} (market median)."
        )
    else:
        classification = "Fair"
        recommendation = (
            f"Your price is within the fair market range "
            f"(MYR {analysis.fair_price_low:.2f}–{analysis.fair_price_high:.2f}). "
            f"Good competitive positioning."
        )

    return MarketPosition(
        user_price=user_price,
        market_median=analysis.median_price,
        percentile=round(percentile, 1),
        classification=classification,
        vs_median_pct=round(vs_median, 1),
        recommendation=recommendation,
        platform_breakdown=platform_prices or [],
    )


def _reconstruct_sorted_prices(analysis: FairPriceAnalysis) -> list[float]:
    """Approximate a sorted price list from summary stats for percentile calculations."""
    # We use a simple linear interpolation from known percentile anchors
    return sorted([
        analysis.min_price,
        analysis.cheap_threshold,
        analysis.median_price,
        analysis.expensive_threshold,
        analysis.max_price,
    ])
