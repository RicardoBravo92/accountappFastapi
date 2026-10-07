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


class PaymentMethod(StrEnum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    CHECK = "check"
    OTHER = "other"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    method: Mapped[str] = mapped_column(String(20), nullable=False, default=PaymentMethod.BANK_TRANSFER)
    reference: Mapped[str] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")

    __table_args__ = (
        Index("idx_payment_company", "company_id"),
        Index("idx_payment_invoice", "invoice_id"),
    )
