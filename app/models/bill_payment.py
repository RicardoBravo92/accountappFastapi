from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
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


class BillPaymentMethod(StrEnum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    CHECK = "check"
    OTHER = "other"


class BillPayment(Base):
    __tablename__ = "bill_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    bill_id: Mapped[int] = mapped_column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    method: Mapped[str] = mapped_column(String(20), nullable=False, default=BillPaymentMethod.BANK_TRANSFER)
    reference: Mapped[str] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    bill: Mapped["Bill"] = relationship("Bill", back_populates="payments")

    __table_args__ = (
        Index("idx_bill_payment_company", "company_id"),
        Index("idx_bill_payment_bill", "bill_id"),
    )
