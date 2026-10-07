"""Upload schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Upload response model."""

    filename: str
    message: str
    size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: Optional[datetime] = None


class UploadListResponse(BaseModel):
    """List of uploads response."""

    files: List[str]
    count: int


class FileDownloadResponse(BaseModel):
    """File download info."""

    filename: str
    content_type: str
    size: int