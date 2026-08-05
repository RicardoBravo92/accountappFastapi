from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default=AccountType.ASSET)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    is_bank: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company: Mapped["Company"] = relationship("Company", back_populates="accounts")
    parent: Mapped[Optional["Account"]] = relationship("Account", remote_side=[id], back_populates="children")
    children: Mapped[list["Account"]] = relationship("Account", back_populates="parent", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="account")
    outgoing_transfers: Mapped[list["Transfer"]] = relationship("Transfer", foreign_keys="[Transfer.from_account_id]", back_populates="from_account")
    incoming_transfers: Mapped[list["Transfer"]] = relationship("Transfer", foreign_keys="[Transfer.to_account_id]", back_populates="to_account")

    __table_args__ = (
        Index("idx_account_company", "company_id"),
        Index("idx_account_code", "code"),
        Index("idx_account_type", "type"),
    )
