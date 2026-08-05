from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
    expires_at: datetime | None = None


class TokenData(BaseModel):
    user_id: int | None = None
    company_id: int | None = None
