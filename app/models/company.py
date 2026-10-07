from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    tax_id: Mapped[str] = mapped_column(String(50), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    date_format: Mapped[str] = mapped_column(String(20), nullable=False, default="Y-m-d")
    financial_year_start: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    users: Mapped[list["UserCompany"]] = relationship(
        "UserCompany", back_populates="company", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact", back_populates="company", cascade="all, delete-orphan"
    )
    accounts: Mapped[list["Account"]] = relationship(
        "Account", back_populates="company", cascade="all, delete-orphan"
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category", back_populates="company", cascade="all, delete-orphan"
    )
    currencies: Mapped[list["Currency"]] = relationship(
        "Currency", back_populates="company", cascade="all, delete-orphan"
    )
    taxes: Mapped[list["Tax"]] = relationship(
        "Tax", back_populates="company", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_company_slug", "slug"),
    )
