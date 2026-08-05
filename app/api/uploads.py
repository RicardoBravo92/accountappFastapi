from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.utils.file_upload import (
    delete_file,
    get_file_path,
    list_upload_files,
    save_upload_file,
    validate_file_size,
    validate_image_upload,
)

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not validate_file_size(file):
        raise HTTPException(status_code=400, detail="File size exceeds limit")

    if file.content_type.startswith("image/"):
        if not validate_image_upload(file):
            raise HTTPException(status_code=400, detail="Invalid image format")

    filename = save_upload_file(file)

    return {"filename": filename, "message": "File uploaded successfully"}


@router.get("/")
def list_uploads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    files = list_upload_files()
    return {"files": files}


@router.get("/{filename}")
def download_file(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = get_file_path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=filename)


@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
def delete_upload(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = delete_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found or could not be deleted")
