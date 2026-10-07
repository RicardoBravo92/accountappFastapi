from datetime import datetime

from app.schemas.sanitized_base import SanitizedBaseModel, SanitizedStr


class CompanyBase(SanitizedBaseModel):
    name: SanitizedStr
    slug: SanitizedStr
    email: SanitizedStr | None = None
    phone: SanitizedStr | None = None
    address: SanitizedStr | None = None
    city: SanitizedStr | None = None
    country: SanitizedStr | None = None
    tax_id: SanitizedStr | None = None
    currency_code: SanitizedStr = "USD"
    date_format: SanitizedStr = "Y-m-d"
    financial_year_start: int | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(SanitizedBaseModel):
    name: SanitizedStr | None = None
    email: SanitizedStr | None = None
    phone: SanitizedStr | None = None
    address: SanitizedStr | None = None
    city: SanitizedStr | None = None
    country: SanitizedStr | None = None
    tax_id: SanitizedStr | None = None
    currency_code: SanitizedStr | None = None
    date_format: SanitizedStr | None = None
    financial_year_start: int | None = None
    is_active: bool | None = None


class CompanyResponse(CompanyBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
