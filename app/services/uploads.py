from fastapi.responses import FileResponse
from PIL import GimpGradientFile
from fastapi import UploadFile
from app.utils.file_upload import (
    delete_file,
    get_file_path,
    list_upload_files,
    save_upload_file,
    validate_file_size,
    validate_image_upload,
)
from fastapi import HTTPException
from fastapi import File , UploadFile 
from app.services.uploads import upload_file

async def upload_file (file: UploadFile = File(...)):
    if not validate_file_size(file):
        raise HTTPException(status_code=400, detail="File size exceeds limit")

    if file.content_type.startswith("image/"):
        if not validate_image_upload(file):
            raise HTTPException(status_code=400, detail="Invalid image format")

    filename = save_upload_file(file)

    return {"filename": filename, "message": "File uploaded successfully"}


async def list_uploads (): 
    return list_upload_files()

async def download_file(filename: str):
    file_path = get_file_path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=filename)

async def delete_upload(filename: str):
    success = delete_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found or could not be deleted")