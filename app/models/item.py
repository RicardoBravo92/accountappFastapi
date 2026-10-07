from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    unit: Mapped[str] = mapped_column(String(20), nullable=True)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    sku: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    company: Mapped["Company"] = relationship("Company")
    category: Mapped[Optional["Category"]] = relationship("Category")

    __table_args__ = (
        Index("idx_item_company", "company_id"),
        Index("idx_item_sku", "sku"),
    )
