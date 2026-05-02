import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tracked_products.id", ondelete="CASCADE"), index=True)

    platform: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    seller_name: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    original_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    discount_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    currency: Mapped[str] = mapped_column(String(10), default="MYR")
    url: Mapped[str | None] = mapped_column(Text)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    review_count: Mapped[int | None]

    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    product: Mapped["TrackedProduct"] = relationship(back_populates="price_snapshots")
