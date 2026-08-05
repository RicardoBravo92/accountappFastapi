from datetime import datetime

from pydantic import BaseModel


class CurrencyBase(BaseModel):
    code: str
    name: str
    symbol: str | None = None
    exchange_rate: float = 1
    is_base: bool = False


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    symbol: str | None = None
    exchange_rate: float | None = None
    is_base: bool | None = None
    is_active: bool | None = None


class CurrencyResponse(CurrencyBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
