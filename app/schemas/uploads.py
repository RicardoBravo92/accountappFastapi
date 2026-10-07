"""Upload schemas."""

from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Upload response model."""

    filename: str
    message: str
    size: int | None = None
    content_type: str | None = None
    created_at: datetime | None = None


class UploadListResponse(BaseModel):
    """List of uploads response."""

    files: list[str]
    count: int


class FileDownloadResponse(BaseModel):
    """File download info."""

    filename: str
    content_type: str
    size: int
