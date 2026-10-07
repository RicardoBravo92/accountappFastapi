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


class BillStatus(StrEnum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    bill_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=BillStatus.DRAFT)
    issue_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    tax_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    discount_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    paid_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    vendor: Mapped["Contact"] = relationship("Contact")
    items: Mapped[list["BillItem"]] = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    payments: Mapped[list["BillPayment"]] = relationship("BillPayment", back_populates="bill", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_bill_company", "company_id"),
        Index("idx_bill_vendor", "vendor_id"),
        Index("idx_bill_status", "status"),
        Index("idx_bill_due_date", "due_date"),
    )
