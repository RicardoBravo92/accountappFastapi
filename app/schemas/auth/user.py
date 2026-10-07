from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    role: str | None = "viewer"


class UserCreate(UserBase):
    password: str = Field(min_length=12, max_length=128, description="Password must be 12-128 characters")

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password meets complexity requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=" for c in v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*()_+-=)")
        return v


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
