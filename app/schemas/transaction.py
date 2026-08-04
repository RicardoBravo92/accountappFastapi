from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionBase(BaseModel):
    account_id: int
    type: str
    amount: float
    currency_code: str = "USD"
    description: Optional[str] = None
    reference: Optional[str] = None
    category_id: Optional[int] = None
    transferred_at: Optional[datetime] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    currency_code: Optional[str] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    category_id: Optional[int] = None
    transferred_at: Optional[datetime] = None
    is_reconciled: Optional[bool] = None


class TransactionResponse(TransactionBase):
    id: int
    company_id: int
    is_reconciled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True