from datetime import datetime

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    slug: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    tax_id: str | None = None
    currency_code: str = "USD"
    date_format: str = "Y-m-d"
    financial_year_start: int | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    tax_id: str | None = None
    currency_code: str | None = None
    date_format: str | None = None
    financial_year_start: int | None = None
    is_active: bool | None = None


class CompanyResponse(CompanyBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
