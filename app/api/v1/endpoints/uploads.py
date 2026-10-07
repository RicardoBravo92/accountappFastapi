from fastapi import APIRouter, Depends, File, Response, status, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    UPLOAD_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.uploads import (
    UploadResponse,
    UploadListResponse,
    FileDownloadResponse,
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
async def list_uploads_endpoint(
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["list"])),
):
    files = await list_uploads()
    return {"files": files, "count": len(files)}


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def create_upload_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["create"])),
):
    return await upload_file(file)


@router.get("/{filename}/info", response_model=FileDownloadResponse)
async def get_file_info_endpoint(
    filename: str,
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["read"])),
):
    return await download_file(filename)


@router.get("/{filename}")
async def download_file_endpoint(
    filename: str,
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["read"])),
):
    from app.services.uploads import get_file_path
    from fastapi.responses import FileResponse
    file_path = get_file_path(filename)
    if not file_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)


@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload_endpoint(
    filename: str,
    current_user: User = Depends(require_permission(UPLOAD_PERMISSIONS["delete"])),
):
    await delete_upload(filename)
    return Response(status_code=status.HTTP_204_NO_CONTENT)