from abc import ABC, abstractmethod

from fastapi import UploadFile

from app.modules.files.schemas import FileUpdate


class IFileService(ABC):
    @abstractmethod
    async def upload_file(self, user_id: str, file: UploadFile):
        pass

    @abstractmethod
    async def update_file(self, file_id: str, data: FileUpdate):
        pass

    @abstractmethod
    async def delete_file(self, user_id: str, file_id: str):
        pass

    @abstractmethod
    async def upload_file_avatar(self, user_id: str, file: UploadFile):
        pass
