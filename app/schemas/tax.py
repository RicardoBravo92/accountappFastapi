from datetime import datetime

from pydantic import BaseModel


class TaxBase(BaseModel):
    name: str
    rate: float
    type: str
    is_compound: bool = False


class TaxCreate(TaxBase):
    pass


class TaxUpdate(BaseModel):
    name: str | None = None
    rate: float | None = None
    type: str | None = None
    is_compound: bool | None = None
    is_active: bool | None = None


class TaxResponse(TaxBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
