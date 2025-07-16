from fastapi import APIRouter, UploadFile

from app.core.response import success_response
from app.core.schemas import CustomResponse
from app.modules.auth.deps import UserDep
from app.modules.files.deps import FileServiceDep
from app.modules.files.schemas import FileCreateRead

files_router = APIRouter(tags=["files"])


@files_router.post("/upload", response_model=CustomResponse[FileCreateRead])
async def upload_file(user: UserDep, file_service: FileServiceDep, file: UploadFile):
    file_id = await file_service.upload_file(user_id=user.id, file=file)
    return success_response(data=FileCreateRead(file_id=file_id), message="File uploaded successfully")


@files_router.delete("/{file_id}", response_model=CustomResponse)
async def delete_file(user: UserDep, file_service: FileServiceDep, file_id: str):
    await file_service.delete_file(user_id=user.id, file_id=file_id)
    return success_response(message="File deleted successfully")
