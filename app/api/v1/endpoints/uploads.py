from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies import get_current_user
from app.core.permissions import (
    UPLOAD_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.uploads import (
    FileDownloadResponse,
    UploadListResponse,
    UploadResponse,
)
from app.services.uploads import (
    list_uploads,
    upload_file,
    download_file,
    delete_upload,
    get_file_path,
)

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.get("/", response_model=UploadListResponse)
def list_uploads_endpoint(
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["list"])),
):
    files = list_uploads()
    return {"files": files, "count": len(files)}


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def create_upload_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["create"])),
):
    return upload_file(file)


@router.get("/{filename}/info", response_model=FileDownloadResponse)
def get_file_info_endpoint(
    filename: str,
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["read"])),
):
    return download_file(filename)


@router.get("/{filename}")
def download_file_endpoint(
    filename: str,
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["read"])),
):
    file_path = get_file_path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)


@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_upload_endpoint(
    filename: str,
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["delete"])),
):
    delete_upload(filename)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
