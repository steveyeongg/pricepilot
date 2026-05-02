import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tracked_products.id", ondelete="CASCADE"), index=True)

    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # price_drop | price_spike | competitor_change | back_in_stock | target_price

    threshold_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    threshold_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    direction: Mapped[str | None] = mapped_column(String(10))  # above | below
    platform_filter: Mapped[str | None] = mapped_column(String(200))  # comma-separated platforms

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product: Mapped["TrackedProduct"] = relationship(back_populates="alerts")
    events: Mapped[list["AlertEvent"]] = relationship(back_populates="alert", cascade="all, delete-orphan")


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"), index=True)

    message: Mapped[str] = mapped_column(Text, nullable=False)
    old_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    new_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    platform: Mapped[str | None] = mapped_column(String(100))
    fired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    alert: Mapped["Alert"] = relationship(back_populates="events")
