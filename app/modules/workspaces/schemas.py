from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator

from app.core.schemas import CustomModel
from app.modules.auth.interface import RegisterBase
from app.modules.users.interface import UserBaseRead


# Workspace Membership
class WorkspaceMemberRoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceMembershipDBCreate(BaseModel):
    role: WorkspaceMemberRoleEnum
    is_active: bool


class WorkspaceMembershipDBUpdate(BaseModel):
    role: WorkspaceMemberRoleEnum | None = None
    is_active: bool | None = None


# Used for workspace members
class WorkspaceMembershipBaseRead(CustomModel):
    role: WorkspaceMemberRoleEnum


# Used for workspace membership
class WorkspaceMembershipRead(WorkspaceMembershipBaseRead):
    is_active: bool


# Workspace Invitation
class WorkspaceInvitationDBCreate(BaseModel):
    workspace_id: str
    invitee_id: str
    inviter_id: str


class WorkspaceInvitationDBUpdate(BaseModel):
    status: str


# Workspace
class WorkspaceDBCreate(BaseModel):
    name: str
    slug: str
    logo: str | None = None


class WorkspaceDBUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    logo: str | None = None
    deleted_at: datetime | None


class WorkspaceCreate(BaseModel):
    name: str
    logo: str | None = None

    @field_validator("name")
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    logo: str | None = None


class WorkspaceMembershipRoleUpdate(BaseModel):
    user_id: str
    role: WorkspaceMemberRoleEnum


class WorkspaceDelete(BaseModel):
    deleted_at: datetime


class WorkspaceTransfer(BaseModel):
    user_id: str


class WorkspaceInvite(BaseModel):
    emails: list[EmailStr]


class WorkspaceSwitch(BaseModel):
    workspace_id: str


class WorkspaceJoin(BaseModel):
    token: str | None
    email: EmailStr | None
    user_data: RegisterBase | None


class WorkspaceReadBase(CustomModel):
    id: str
    name: str
    slug: str
    logo: str | None


class WorkspaceMemberRead(UserBaseRead, WorkspaceMembershipBaseRead):
    pass


class WorkspaceRead(WorkspaceReadBase):
    membership: WorkspaceMembershipRead


class WorkspaceDetailRead(WorkspaceRead):
    members: list[WorkspaceMemberRead]


class WorkspaceCreateRead(BaseModel):
    workspace_id: str
