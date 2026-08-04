from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


class TokenData(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None