"""
APScheduler background jobs:
- Price check: periodically re-scrape all tracked products
- Alert check: evaluate alerts against latest prices and fire events
"""
import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.product import TrackedProduct
from app.models.price import PriceSnapshot
from app.models.alert import Alert, AlertEvent
from app.scrapers import search_all

log = logging.getLogger(__name__)
settings = get_settings()

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Asia/Kuala_Lumpur")
    return _scheduler


async def _run_price_checks():
    """Re-scrape all tracked products and store new PriceSnapshots."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(TrackedProduct))
        products = result.scalars().all()

        for product in products:
            query = product.search_query or product.name
            try:
                raw = await search_all(query, limit_per_platform=5)
                for r in raw:
                    if not r.get("price") or float(r["price"]) <= 0:
                        continue
                    snap = PriceSnapshot(
                        product_id=product.id,
                        platform=r["platform"],
                        seller_name=r.get("seller_name"),
                        price=float(r["price"]),
                        original_price=float(r["original_price"]) if r.get("original_price") else None,
                        discount_pct=r.get("discount_pct"),
                        url=r.get("url"),
                        in_stock=r.get("in_stock", True),
                        rating=r.get("rating"),
                        review_count=r.get("review_count"),
                    )
                    db.add(snap)
                log.info("Price check OK: %s — %d results", product.name, len(raw))
            except Exception as exc:
                log.warning("Price check failed for %s: %s", product.name, exc)

        await db.commit()


async def _run_alert_checks():
    """Evaluate active alerts against the latest price snapshots."""
    async with AsyncSessionLocal() as db:
        alerts_result = await db.execute(
            select(Alert).where(Alert.is_active == True)
        )
        alerts = alerts_result.scalars().all()

        for alert in alerts:
            try:
                await _evaluate_alert(db, alert)
            except Exception as exc:
                log.warning("Alert check failed for %s: %s", alert.id, exc)

        await db.commit()


async def _evaluate_alert(db: AsyncSession, alert: Alert):
    # Get two most recent snapshots to detect changes
    filters = [PriceSnapshot.product_id == alert.product_id]
    if alert.platform_filter:
        platforms = [p.strip() for p in alert.platform_filter.split(",")]
        filters.append(PriceSnapshot.platform.in_(platforms))

    result = await db.execute(
        select(PriceSnapshot)
        .where(and_(*filters))
        .order_by(PriceSnapshot.captured_at.desc())
        .limit(10)
    )
    snapshots = result.scalars().all()
    if len(snapshots) < 2:
        return

    latest = snapshots[0]
    previous_prices = [float(s.price) for s in snapshots[1:]]
    prev_avg = sum(previous_prices) / len(previous_prices)
    curr_price = float(latest.price)

    fired = False
    message = ""
    old_price = round(prev_avg, 2)
    new_price = round(curr_price, 2)

    if alert.alert_type == "price_drop":
        if alert.threshold_pct and prev_avg > 0:
            drop_pct = (prev_avg - curr_price) / prev_avg * 100
            if drop_pct >= alert.threshold_pct:
                fired = True
                message = f"Price dropped {drop_pct:.1f}% on {latest.platform} to MYR {curr_price:.2f}"

    elif alert.alert_type == "price_spike":
        if alert.threshold_pct and prev_avg > 0:
            spike_pct = (curr_price - prev_avg) / prev_avg * 100
            if spike_pct >= alert.threshold_pct:
                fired = True
                message = f"Price spiked {spike_pct:.1f}% on {latest.platform} to MYR {curr_price:.2f}"

    elif alert.alert_type == "target_price":
        if alert.threshold_price:
            if alert.direction == "below" and curr_price <= alert.threshold_price:
                fired = True
                message = f"Price hit MYR {curr_price:.2f} on {latest.platform} (target ≤ {alert.threshold_price:.2f})"
            elif alert.direction == "above" and curr_price >= alert.threshold_price:
                fired = True
                message = f"Price hit MYR {curr_price:.2f} on {latest.platform} (target ≥ {alert.threshold_price:.2f})"

    elif alert.alert_type == "back_in_stock":
        prev_stocks = [s.in_stock for s in snapshots[1:]]
        if not any(prev_stocks) and latest.in_stock:
            fired = True
            message = f"Back in stock on {latest.platform} at MYR {curr_price:.2f}"

    if fired:
        event = AlertEvent(
            alert_id=alert.id,
            message=message,
            old_price=old_price,
            new_price=new_price,
            platform=latest.platform,
        )
        db.add(event)
        alert.last_triggered = datetime.now(timezone.utc)
        log.info("Alert fired: %s", message)


def start_scheduler():
    sched = get_scheduler()
    sched.add_job(
        _run_price_checks,
        "interval",
        minutes=settings.price_check_interval_minutes,
        id="price_checks",
        replace_existing=True,
    )
    sched.add_job(
        _run_alert_checks,
        "interval",
        minutes=settings.alert_check_interval_minutes,
        id="alert_checks",
        replace_existing=True,
    )
    sched.start()
    log.info("Scheduler started (price every %dm, alerts every %dm)",
             settings.price_check_interval_minutes, settings.alert_check_interval_minutes)


def stop_scheduler():
    sched = get_scheduler()
    if sched.running:
        sched.shutdown(wait=False)
