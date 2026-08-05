from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_current_user
from app.models.auth.user import User
from app.services.uploads import upload_service

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.get("/")
def list_uploads(
    current_user: User = Depends(get_current_user),
):
    return upload_service["list_uploads"]()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    return upload_service["upload_file"](file)


@router.get("/{filename}")
def download_file(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    return upload_service["download_file"](filename)


@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
def delete_upload(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    return upload_service["delete_upload"](filename)
