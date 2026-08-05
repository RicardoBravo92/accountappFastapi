from datetime import datetime

from pydantic import BaseModel


class TransferBase(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    currency_code: str = "USD"
    description: str | None = None
    reference: str | None = None
    transferred_at: datetime


class TransferCreate(TransferBase):
    pass


class TransferUpdate(BaseModel):
    from_account_id: int | None = None
    to_account_id: int | None = None
    amount: float | None = None
    currency_code: str | None = None
    description: str | None = None
    reference: str | None = None
    transferred_at: datetime | None = None
    is_reconciled: bool | None = None


class TransferResponse(TransferBase):
    id: int
    company_id: int
    is_reconciled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
