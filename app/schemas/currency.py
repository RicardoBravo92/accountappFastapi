from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CurrencyBase(BaseModel):
    code: str
    name: str
    symbol: Optional[str] = None
    exchange_rate: float = 1
    is_base: bool = False


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    exchange_rate: Optional[float] = None
    is_base: Optional[bool] = None
    is_active: Optional[bool] = None


class CurrencyResponse(CurrencyBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True