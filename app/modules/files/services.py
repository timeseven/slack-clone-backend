import boto3
from fastapi import UploadFile

from app.core.config import settings
from app.core.utils import generate_short_id
from app.modules.files.exceptions import FileBadRequest, FilePermissionDenied
from app.modules.files.interface import IFileService
from app.modules.files.repos import FileRepo
from app.modules.files.schemas import FileUpdate


class FileService(IFileService):
    def __init__(self, file_repo: FileRepo, s3_client: boto3.client):
        self.file_repo = file_repo
        self.s3_client = s3_client

    def generate_s3_url(self, file_key: str) -> str:
        return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"

    async def upload_file_s3(self, file_key: str, file: UploadFile):
        try:
            content = await file.read()
            self.s3_client.put_object(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=file_key,
                Body=content,
                ContentType=file.content_type,
            )
            return {
                "key": file_key,
                "url": self.generate_s3_url(file_key),
                "filename": file_key,
                "content_type": file.content_type,
                "size": len(content),
            }
        except Exception:
            raise FileBadRequest

    async def delete_file_s3(self, file_key: str):
        self.s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=file_key)

    async def update_file(self, file_id: str, data: FileUpdate):
        try:
            print("data>>>", data)
            return await self.file_repo.update(file_id, data=data.model_dump(exclude_unset=True))
        except Exception as e:
            raise FileBadRequest(detail=str(e))

    async def upload_file(self, user_id: str, file: UploadFile):
        file_id = generate_short_id()
        file_ext = file.filename.split(".")[-1]
        file_key = f"{file_id}.{file_ext}"

        file_info = await self.upload_file_s3(file_key, file)
        try:
            await self.file_repo.create(
                file_id=file_id,
                data={
                    "filename": file_info["filename"],
                    "filepath": file_info["url"],
                    "filetype": file_info["content_type"],
                    "size": file_info["size"],
                    "uploader_id": user_id,
                },
            )
            return file_id
        except Exception:
            await self.delete_file_s3(file_key)
            raise FileBadRequest

    async def delete_file(self, user_id: str, file_id: str):
        file = await self.file_repo.get_one_by_id(file_id)
        if file:
            if file.uploader_id != user_id:
                raise FilePermissionDenied(detail="You can't delete this photo")
            await self.delete_file_s3(file.filepath)
            try:
                await self.file_repo.delete(file_id)
            except Exception:
                raise FileBadRequest

    async def upload_file_avatar(self, user_id: str, file: UploadFile):
        file_key = f"avatar/{user_id}/{file.filename}"
        file_info = await self.upload_file_s3(file_key, file)
        return file_info["url"]
