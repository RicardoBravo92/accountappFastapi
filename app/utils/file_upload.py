import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from app.config import settings


def ensure_uploads_dir():
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def generate_filename(original_filename: str) -> str:
    file_extension = Path(original_filename).suffix
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    return unique_filename


def save_upload_file(upload_file: UploadFile) -> str:
    ensure_uploads_dir()
    filename = generate_filename(upload_file.filename)
    file_path = Path(settings.UPLOAD_DIR) / filename

    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())

    return filename


def validate_image_upload(file: UploadFile) -> bool:
    try:
        image = Image.open(file.file)
        image.verify()
        image.close()
        return True
    except Exception:
        return False


def validate_file_size(file: UploadFile, max_size: int = settings.MAX_UPLOAD_SIZE) -> bool:
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    return file_size <= max_size


def get_file_path(filename: str) -> Path:
    return Path(settings.UPLOAD_DIR) / filename


def delete_file(filename: str) -> bool:
    try:
        file_path = get_file_path(filename)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception:
        return False


def list_upload_files() -> list[str]:
    ensure_uploads_dir()
    return [f.name for f in Path(settings.UPLOAD_DIR).iterdir() if f.is_file()]
