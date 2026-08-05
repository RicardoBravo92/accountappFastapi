from datetime import datetime

from pydantic import BaseModel


class AccountBase(BaseModel):
    code: str
    name: str
    type: str
    parent_id: int | None = None
    is_bank: bool = False


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    type: str | None = None
    parent_id: int | None = None
    is_bank: bool | None = None
    is_active: bool | None = None


class AccountResponse(AccountBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
