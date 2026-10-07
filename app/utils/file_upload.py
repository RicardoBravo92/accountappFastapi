import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.config import settings

# Allowed MIME types for uploads
ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    # Text
    "text/plain",
}

# MIME types mapped to expected extensions for validation
MIME_EXTENSION_MAP = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/gif": [".gif"],
    "image/webp": [".webp"],
    "image/svg+xml": [".svg"],
    "application/pdf": [".pdf"],
    "application/msword": [".doc"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.ms-excel": [".xls"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "text/csv": [".csv"],
    "text/plain": [".txt"],
}


def ensure_uploads_dir():
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def generate_secure_filename(original_filename: str, mime_type: str | None = None) -> str:
    """Generate a secure filename with UUID and validated extension.

    Args:
        original_filename: Original filename from user
        mime_type: Optional MIME type to validate extension against

    Returns:
        Secure filename with UUID and appropriate extension
    """
    # Extract extension from original filename
    original_ext = Path(original_filename).suffix.lower()

    # If MIME type provided, validate extension matches expected
    if mime_type and mime_type in MIME_EXTENSION_MAP:
        allowed_extensions = MIME_EXTENSION_MAP[mime_type]
        if original_ext not in allowed_extensions:
            # Use first allowed extension for this MIME type
            original_ext = allowed_extensions[0]

    # Ensure extension is safe (no path traversal)
    original_ext = "".join(c for c in original_ext if c.isalnum() or c == ".")

    # Generate UUID-based filename
    unique_filename = f"{uuid.uuid4().hex}{original_ext}"
    return unique_filename


def validate_mime_type(file: UploadFile) -> bool:
    """Validate that the uploaded file's MIME type is allowed.

    Args:
        file: UploadFile object

    Returns:
        True if MIME type is allowed, False otherwise
    """
    content_type = file.content_type
    if not content_type:
        return False

    # Normalize MIME type (remove charset, etc.)
    mime_type = content_type.split(";")[0].strip().lower()
    return mime_type in ALLOWED_MIME_TYPES


def validate_file_extension(filename: str, mime_type: str | None = None) -> bool:
    """Validate file extension against allowed list and MIME type.

    Args:
        filename: Original filename
        mime_type: Optional MIME type to cross-reference

    Returns:
        True if extension is allowed, False otherwise
    """
    ext = Path(filename).suffix.lower()
    if not ext:
        return False

    # Check if extension is in allowed map values
    allowed_extensions = set()
    for exts in MIME_EXTENSION_MAP.values():
        allowed_extensions.update(exts)

    if ext not in allowed_extensions:
        return False

    # If MIME type provided, cross-reference
    if mime_type and mime_type in MIME_EXTENSION_MAP:
        return ext in MIME_EXTENSION_MAP[mime_type]

    return True


def validate_file_size(file: UploadFile, max_size: int = settings.MAX_UPLOAD_SIZE) -> bool:
    """Validate file size does not exceed maximum.

    Args:
        file: UploadFile object
        max_size: Maximum allowed size in bytes

    Returns:
        True if size is within limit, False otherwise
    """
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    return file_size <= max_size


def validate_image_upload(file: UploadFile) -> bool:
    """Validate that an uploaded image is valid and safe.

    Args:
        file: UploadFile object

    Returns:
        True if image is valid, False otherwise
    """
    try:
        # Reset file pointer
        file.file.seek(0)
        image = Image.open(file.file)
        image.verify()  # Verify it's a valid image
        image.close()
        file.file.seek(0)
        return True
    except (UnidentifiedImageError, Exception):
        return False


def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file with full validation.

    Args:
        upload_file: UploadFile object

    Returns:
        Secure filename of saved file

    Raises:
        HTTPException: If validation fails
    """
    # Validate MIME type
    if not validate_mime_type(upload_file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{upload_file.content_type}' not allowed. "
                   f"Allowed types: {', '.join(sorted(ALLOWED_MIME_TYPES))}",
        )

    # Validate file extension
    if not validate_file_extension(upload_file.filename, upload_file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File extension not allowed or doesn't match content type",
        )

    # Validate file size
    if not validate_file_size(upload_file):
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {max_mb:.0f}MB",
        )

    # Validate image if applicable
    if upload_file.content_type and upload_file.content_type.startswith("image/"):
        if not validate_image_upload(upload_file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted image file",
            )

    # Generate secure filename
    ensure_uploads_dir()
    filename = generate_secure_filename(upload_file.filename, upload_file.content_type)
    file_path = Path(settings.UPLOAD_DIR) / filename

    # Prevent path traversal (should be redundant with secure filename, but defense in depth)
    try:
        file_path.resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename",
        ) from err

    # Save file
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())

    return filename


def get_file_path(filename: str) -> Path:
    """Get secure file path, preventing path traversal.

    Args:
        filename: Filename to resolve

    Returns:
        Path object within upload directory

    Raises:
        HTTPException: If path traversal detected
    """
    file_path = Path(settings.UPLOAD_DIR) / filename

    # Prevent path traversal
    try:
        file_path.resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path",
        ) from err

    return file_path


def delete_file(filename: str) -> bool:
    """Delete a file securely.

    Args:
        filename: Filename to delete

    Returns:
        True if deleted, False if not found or error
    """
    try:
        file_path = get_file_path(filename)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except HTTPException:
        return False
    except Exception:
        return False


def list_upload_files() -> list[str]:
    """List all uploaded files.

    Returns:
        List of filenames
    """
    ensure_uploads_dir()
    return [f.name for f in Path(settings.UPLOAD_DIR).iterdir() if f.is_file()]
