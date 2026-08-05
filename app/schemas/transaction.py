from datetime import datetime

from pydantic import BaseModel


class TransactionBase(BaseModel):
    account_id: int
    type: str
    amount: float
    currency_code: str = "USD"
    description: str | None = None
    reference: str | None = None
    category_id: int | None = None
    transferred_at: datetime | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    account_id: int | None = None
    type: str | None = None
    amount: float | None = None
    currency_code: str | None = None
    description: str | None = None
    reference: str | None = None
    category_id: int | None = None
    transferred_at: datetime | None = None
    is_reconciled: bool | None = None


class TransactionResponse(TransactionBase):
    id: int
    company_id: int
    is_reconciled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
