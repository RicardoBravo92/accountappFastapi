from datetime import datetime

from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    unit_price: float = 0
    unit: str | None = None
    category_id: int | None = None
    tax_rate: float = 0
    sku: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    unit_price: float | None = None
    unit: str | None = None
    category_id: int | None = None
    tax_rate: float | None = None
    sku: str | None = None
    is_active: bool | None = None


class ItemResponse(ItemBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
