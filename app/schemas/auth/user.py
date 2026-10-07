from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.sanitized_base import SanitizedBaseModel, SanitizedStr


class UserBase(SanitizedBaseModel):
    email: SanitizedStr
    username: SanitizedStr
    first_name: SanitizedStr
    last_name: SanitizedStr
    role: SanitizedStr | None = "viewer"


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


class UserUpdate(SanitizedBaseModel):
    email: SanitizedStr | None = None
    username: SanitizedStr | None = None
    first_name: SanitizedStr | None = None
    last_name: SanitizedStr | None = None
    role: SanitizedStr | None = None
    is_active: bool | None = None


class UserLogin(SanitizedBaseModel):
    email: SanitizedStr
    password: str  # Don't sanitize password - it would break validation


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
