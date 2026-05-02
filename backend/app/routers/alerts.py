import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import Alert, AlertEvent
from app.schemas.alert import AlertCreate, AlertOut, AlertEventOut

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
async def list_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).order_by(Alert.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
async def create_alert(body: AlertCreate, db: AsyncSession = Depends(get_db)):
    alert = Alert(**body.model_dump())
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    a = await db.get(Alert, alert_id)
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    return a


@router.patch("/{alert_id}/toggle", response_model=AlertOut)
async def toggle_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    a = await db.get(Alert, alert_id)
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    a.is_active = not a.is_active
    await db.flush()
    await db.refresh(a)
    return a


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    a = await db.get(Alert, alert_id)
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.delete(a)


@router.get("/events/recent", response_model=list[AlertEventOut])
async def recent_alert_events(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AlertEvent).order_by(AlertEvent.fired_at.desc()).limit(limit)
    )
    return result.scalars().all()
