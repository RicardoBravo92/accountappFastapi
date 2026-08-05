from datetime import datetime

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    type: str
    color: str | None = None
    icon: str | None = None
    parent_id: int | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    color: str | None = None
    icon: str | None = None
    parent_id: int | None = None
    is_active: bool | None = None


class CategoryResponse(CategoryBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
