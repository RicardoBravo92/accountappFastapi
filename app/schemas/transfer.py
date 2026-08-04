from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransferBase(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    currency_code: str = "USD"
    description: Optional[str] = None
    reference: Optional[str] = None
    transferred_at: datetime


class TransferCreate(TransferBase):
    pass


class TransferUpdate(BaseModel):
    from_account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    amount: Optional[float] = None
    currency_code: Optional[str] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    transferred_at: Optional[datetime] = None
    is_reconciled: Optional[bool] = None


class TransferResponse(TransferBase):
    id: int
    company_id: int
    is_reconciled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True