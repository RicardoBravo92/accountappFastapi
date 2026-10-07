from datetime import datetime, UTC
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    BANKING = "banking"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    PRODUCT = "product"
    SERVICE = "service"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default=CategoryType.EXPENSE)
    color: Mapped[str] = mapped_column(String(7), nullable=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    company: Mapped["Company"] = relationship("Company", back_populates="categories")
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id])
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="category")

    __table_args__ = (
        Index("idx_category_company", "company_id"),
        Index("idx_category_type", "type"),
    )
