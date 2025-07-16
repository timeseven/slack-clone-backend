from datetime import datetime, timezone

import jwt
from fastapi import UploadFile
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from loguru import logger
from pydantic import EmailStr
from sqlalchemy import Row
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.utils import compute_update_fields_from_dict, generate_short_id, verify_password
from app.modules.files.interface import IFileService
from app.modules.users.exceptions import (
    UserBadRequest,
    UserEmailValidationError,
    UserInvalidCredentials,
    UserPasswordValidationError,
)
from app.modules.users.interface import IUserService
from app.modules.users.repos import UserRepo
from app.modules.users.schemas import UserDBCreate, UserDBUpdate


class UserService(IUserService):
    def __init__(self, user_repo: UserRepo, file_service: IFileService):
        self.user_repo = user_repo
        self.file_service = file_service

    async def get_user_by_email(self, email: EmailStr) -> Row:
        try:
            return await self.user_repo.get_one_by_email(email)
        except Exception as e:
            raise UserBadRequest(detail=str(e))

    async def get_users_by_emails(self, emails: list[EmailStr]) -> list[Row]:
        try:
            return await self.user_repo.get_list_by_emails(emails)
        except Exception as e:
            raise UserBadRequest(detail=str(e))

    async def get_user_by_id(self, user_id: str) -> Row:
        try:
            return await self.user_repo.get_one_by_id(user_id)
        except Exception as e:
            raise UserBadRequest(detail=str(e))

    async def get_users_by_ids(self, user_ids) -> list[Row]:
        try:
            return await self.user_repo.get_list_by_ids(user_ids)
        except Exception as e:
            raise UserBadRequest(detail=str(e))

    async def create_user(self, data: UserDBCreate) -> str:
        existing = await self.get_user_by_email(data.email)
        if existing:
            raise UserEmailValidationError("Email already exists")
        try:
            user_id = generate_short_id(prefix="U")
            await self.user_repo.create(user_id=user_id, data=data.model_dump())
            return user_id
        except IntegrityError as e:
            raise UserEmailValidationError("Email already exists") from e

    async def update_user(self, user_id: str, data: UserDBUpdate) -> Row:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserBadRequest("User not found")

        update_data = compute_update_fields_from_dict(
            old=user,
            new_data=data.model_dump(),
            include_none_fields=["status", "deleted_at"],
        )

        if not update_data:
            return user

        try:
            return await self.user_repo.update(user_id, data=update_data)
        except Exception as e:
            logger.exception("Failed to update user")
            raise UserBadRequest(detail=str(e))

    async def upload_avatar(self, user_id: str, file: UploadFile) -> Row:
        avatar_url = await self.file_service.upload_file_avatar(user_id=user_id, file=file)
        return await self.update_user(user_id=user_id, data=UserDBUpdate(avatar=avatar_url))

    async def authenticate_user(self, email: EmailStr, password: str) -> Row:
        user = await self.get_user_by_email(email)
        if not user:
            raise UserEmailValidationError("User not found with this email")
        if not user.is_verified:
            raise UserEmailValidationError("User not verified")
        if not verify_password(password, user.hashed_password):
            raise UserPasswordValidationError("Wrong password")

        return user

    async def get_user_from_token(self, token: str, secret_key: str) -> Row:
        try:
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[settings.ALGORITHM],
            )
            user_id = str(payload.get("sub"))
            if not user_id:
                raise UserInvalidCredentials
        except (DecodeError, ExpiredSignatureError, InvalidTokenError):
            raise UserInvalidCredentials

        user = await self.get_user_by_id(user_id=user_id)

        if not user:
            raise UserInvalidCredentials
        if not user.is_verified:
            raise UserInvalidCredentials(detail="Unverified user")

        return user

    async def delete_user(self, user_id: str):
        try:
            await self.update_user(user_id=user_id, data=UserDBUpdate(deleted_at=datetime.now(tz=timezone.utc)))
        except Exception as e:
            raise UserBadRequest(detail=str(e))
