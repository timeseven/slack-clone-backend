from abc import ABC, abstractmethod

from fastapi import UploadFile
from pydantic import EmailStr

from app.modules.users.schemas import (
    UserBaseRead,  # noqa F401
    UserDBCreate,
    UserDBUpdate,
    UserRead,  # noqa F401
)


class IUserService(ABC):
    @abstractmethod
    async def get_user_by_email(self, email: EmailStr):
        pass

    @abstractmethod
    async def get_users_by_emails(self, emails: list[EmailStr]):
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str):
        pass

    @abstractmethod
    async def get_users_by_ids(self, user_ids: list[str]):
        pass

    @abstractmethod
    async def create_user(self, data: UserDBCreate):
        pass

    @abstractmethod
    async def update_user(self, user_id: str, data: UserDBUpdate):
        pass

    @abstractmethod
    async def upload_avatar(self, user_id: str, file: UploadFile):
        pass

    @abstractmethod
    async def authenticate_user(self, email: EmailStr, password: str):
        pass

    @abstractmethod
    async def get_user_from_token(self, token: str, secret_key: str):
        pass

    @abstractmethod
    async def delete_user(self, user_id: str):
        pass
