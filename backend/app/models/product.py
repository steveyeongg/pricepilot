import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class TrackedProduct(Base):
    __tablename__ = "tracked_products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(200))
    category: Mapped[str | None] = mapped_column(String(100))
    barcode: Mapped[str | None] = mapped_column(String(100), index=True)
    image_url: Mapped[str | None] = mapped_column(Text)
    search_query: Mapped[str | None] = mapped_column(String(500))

    # User's own pricing data (for sellers)
    user_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    user_cost: Mapped[float | None] = mapped_column(Numeric(10, 2))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    price_snapshots: Mapped[list["PriceSnapshot"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="product", cascade="all, delete-orphan")
