from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    role: str | None = "viewer"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
