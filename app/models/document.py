from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    APPROVED = "approved"
    CANCELLED = "cancelled"


class DocumentType(str, Enum):
    INVOICE = "invoice"
    BILL = "bill"
    RECEIPT = "receipt"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    QUOTATION = "quotation"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default=DocumentType.INVOICE)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=DocumentStatus.DRAFT)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    tax_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    discount_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_document_company", "company_id"),
        Index("idx_document_type", "type"),
        Index("idx_document_status", "status"),
        Index("idx_document_number", "document_number"),
    )
