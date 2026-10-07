from datetime import datetime

from fastapi import File, HTTPException, UploadFile

from app.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.file_upload import (
    delete_file,
    get_file_path,
    list_upload_files,
    save_upload_file,
    validate_file_size,
    validate_image_upload,
    validate_mime_type,
)


async def upload_file(file: UploadFile = File(...)):
    """Upload a file with full validation."""
    # Validate MIME type
    if not validate_mime_type(file):
        raise ValidationError(
            f"File type '{file.content_type}' not allowed",
            field="file",
        )

    # Validate file size
    if not validate_file_size(file):
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise ValidationError(
            f"File size exceeds maximum allowed size of {max_mb:.0f}MB",
            field="file",
        )

    # Validate image if applicable
    if file.content_type and file.content_type.startswith("image/"):
        if not validate_image_upload(file):
            raise ValidationError("Invalid or corrupted image file", field="file")

    # Save file (includes all other validations)
    filename = save_upload_file(file)
    file_path = get_file_path(filename)
    stat = file_path.stat()

    return {
        "filename": filename,
        "message": "File uploaded successfully",
        "size": stat.st_size,
        "content_type": file.content_type,
        "created_at": datetime.fromtimestamp(stat.st_ctime),
    }


async def list_uploads():
    files = list_upload_files()
    return {"files": files, "count": len(files)}


async def download_file(filename: str):
    try:
        file_path = get_file_path(filename)
    except HTTPException as e:
        raise NotFoundError("File", filename) from e

    if not file_path.exists():
        raise NotFoundError("File", filename)

    stat = file_path.stat()
    # Return metadata for response model
    return {
        "filename": filename,
        "content_type": "application/octet-stream",  # Will be detected by FileResponse
        "size": stat.st_size,
    }


async def delete_upload(filename: str):
    success = delete_file(filename)
    if not success:
        raise NotFoundError("File", filename)
    return {"message": "File deleted successfully"}


upload_service = {
    "upload_file": upload_file,
    "list_uploads": list_uploads,
    "download_file": download_file,
    "delete_upload": delete_upload,
    "get_file_path": get_file_path,
}
