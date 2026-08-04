from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BillItemBase(BaseModel):
    item_id: Optional[int] = None
    description: str
    quantity: float = 1
    price: float = 0
    tax_rate: float = 0
    discount: float = 0
    sort_order: int = 0


class BillItemCreate(BillItemBase):
    pass


class BillItemResponse(BillItemBase):
    id: int
    bill_id: int
    tax_amount: float
    total: float
    created_at: datetime

    class Config:
        from_attributes = True


class BillBase(BaseModel):
    vendor_id: int
    bill_number: str
    issue_date: datetime
    due_date: datetime
    currency_code: str = "USD"
    notes: Optional[str] = None


class BillCreate(BillBase):
    items: list[BillItemCreate]


class BillUpdate(BaseModel):
    vendor_id: Optional[int] = None
    bill_number: Optional[str] = None
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    currency_code: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class BillResponse(BillBase):
    id: int
    company_id: int
    status: str
    subtotal: float
    tax_total: float
    discount_total: float
    total: float
    paid_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True