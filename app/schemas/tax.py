from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaxBase(BaseModel):
    name: str
    rate: float
    type: str
    is_compound: bool = False


class TaxCreate(TaxBase):
    pass


class TaxUpdate(BaseModel):
    name: Optional[str] = None
    rate: Optional[float] = None
    type: Optional[str] = None
    is_compound: Optional[bool] = None
    is_active: Optional[bool] = None


class TaxResponse(TaxBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True