from datetime import UTC, datetime
from enum import StrEnum
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


class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default=TransactionType.DEPOSIT)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    reference: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    transferred_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_reconciled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="transactions")

    __table_args__ = (
        Index("idx_transaction_company", "company_id"),
        Index("idx_transaction_account", "account_id"),
        Index("idx_transaction_type", "type"),
        Index("idx_transaction_date", "transferred_at"),
    )
