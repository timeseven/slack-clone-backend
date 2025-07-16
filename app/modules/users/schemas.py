from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.core.schemas import CustomModel


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    avatar: str | None = None
    status: str | None = None


class UserDBCreate(BaseModel):
    email: EmailStr
    hashed_password: str | None = None
    full_name: str


class UserDBUpdate(BaseModel):
    full_name: str | None = None
    avatar: str | None = None
    status: str | None = None
    is_verified: bool | None = None
    hashed_password: str | None = None
    last_login_at: datetime | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    deleted_at: datetime | None = None


# Used for workspace members and channel members
class UserBaseRead(CustomModel):
    id: str
    email: EmailStr
    full_name: str
    avatar: str | None
    status: str | None
    is_active: bool


# Used for user profile
class UserRead(UserBaseRead):
    is_verified: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
