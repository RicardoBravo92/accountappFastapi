from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RecurringFrequency(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Recurring(Base):
    __tablename__ = "recurring"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    document_id: Mapped[int] = mapped_column(Integer, nullable=False)
    document_type: Mapped[str] = mapped_column(String(20), nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False, default=RecurringFrequency.MONTHLY)
    interval: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_generated: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_run: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    __table_args__ = (
        Index("idx_recurring_company", "company_id"),
        Index("idx_recurring_next_run", "next_run"),
    )
