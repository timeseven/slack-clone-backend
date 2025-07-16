from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.core.schemas import CustomModel
from app.modules.users.interface import UserRead


class ChannelTypeEnum(str, Enum):
    CHANNEL = "channel"
    DM = "dm"
    GROUP_DM = "group_dm"


class ChannelMemberRoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ChannelCreate(BaseModel):
    name: str
    description: str | None = None
    type: ChannelTypeEnum | None = None
    template: str | None = None
    is_private: bool | None = None


class ChannelUpdate(BaseModel):
    description: str | None = None
    is_private: bool | None = None


class ChannelDelete(BaseModel):
    deleted_at: datetime


class ChannelTransfer(BaseModel):
    user_id: str


class ChannelMembershipCreate(BaseModel):
    role: ChannelMemberRoleEnum


class ChannelMembershipUpdate(BaseModel):
    last_read_at: datetime | None = None
    unread_count: int | None = None
    role: ChannelMemberRoleEnum | None = None
    is_starred: bool | None = None
    is_muted: bool | None = None


class ChannelMembershipRoleUpdate(BaseModel):
    user_id: str
    role: ChannelMemberRoleEnum


class ChannelMembershipReadBase(CustomModel):
    role: ChannelMemberRoleEnum
    is_starred: bool
    is_muted: bool
    unread_count: int
    last_read_at: datetime | None
    created_at: datetime


class ChannelMemberRead(UserRead, ChannelMembershipReadBase):
    pass


class ChannelReadBase(CustomModel):
    id: str
    workspace_id: str
    name: str | None
    description: str | None
    type: ChannelTypeEnum
    is_private: bool
    created_at: datetime


class ChannelRead(ChannelReadBase):
    membership: ChannelMembershipReadBase | None
    members: list[ChannelMemberRead]


class ChannelCreateRead(BaseModel):
    channel_id: str
