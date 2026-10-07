from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(3), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=True)
    exchange_rate: Mapped[float] = mapped_column(Numeric(15, 6), nullable=False, default=1)
    is_base: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    company: Mapped["Company"] = relationship("Company")

    __table_args__ = (
        Index("idx_currency_company", "company_id"),
        Index("idx_currency_code", "code"),
    )
