from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BillItem(Base):
    __tablename__ = "bill_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bill_id: Mapped[int] = mapped_column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("items.id", ondelete="SET NULL"), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False, default=1)
    price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    discount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    bill: Mapped["Bill"] = relationship("Bill", back_populates="items")
    item: Mapped[Optional["Item"]] = relationship("Item")

    __table_args__ = (
        Index("idx_bill_item_bill", "bill_id"),
    )
