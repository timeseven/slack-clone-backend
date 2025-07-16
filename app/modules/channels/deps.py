from typing import Annotated, Callable

from fastapi import Depends
from sqlalchemy import Row

from app.core.deps import DBConnDep
from app.modules.channels.exceptions import (
    ChannelMembershipNotFound,
    ChannelMembershipPermissionDenied,
    ChannelNotFound,
)
from app.modules.channels.interface import IChannelService
from app.modules.channels.repos import ChannelMembershipRepo, ChannelRepo
from app.modules.channels.services import ChannelService
from app.modules.notifications.realtime.deps import RealTimeNotificationServiceDep
from app.modules.users.deps import UserServiceDep
from app.modules.workspaces.deps import WorkspaceServiceDep, WSMemberDep


async def get_channel_repo(db: DBConnDep):
    return ChannelRepo(db)


ChannelRepoDep = Annotated[ChannelRepo, Depends(get_channel_repo)]


async def get_channel_membership_repo(db: DBConnDep):
    return ChannelMembershipRepo(db)


ChannelMembershipRepoDep = Annotated[ChannelMembershipRepo, Depends(get_channel_membership_repo)]


async def get_channel_service(
    db: DBConnDep,
    channel_repo: ChannelRepoDep,
    channel_membership_repo: ChannelMembershipRepoDep,
    workspace_service: WorkspaceServiceDep,
    user_service: UserServiceDep,
    real_time_notification_service: RealTimeNotificationServiceDep,
) -> IChannelService:
    return ChannelService(
        db=db,
        channel_repo=channel_repo,
        channel_membership_repo=channel_membership_repo,
        workspace_service=workspace_service,
        user_service=user_service,
        real_time_notification_service=real_time_notification_service,
    )


ChannelServiceDep = Annotated[IChannelService, Depends(get_channel_service)]

VALID_ROLES = {"owner", "admin", "member"}


def get_channel_member_with_roles(required_roles: list[str]) -> Callable:
    assert all(role in VALID_ROLES for role in required_roles), "Invalid role in required_roles"

    async def _dep(
        ws_member: WSMemberDep,
        channel_service: ChannelServiceDep,
        channel_id: str,
    ):
        if channel_id is None:
            raise ChannelNotFound

        channel = await channel_service.get_channel(
            workspace_id=ws_member.workspace_id, channel_id=channel_id, user_id=ws_member.user_id
        )
        membership = channel.get("membership")

        if channel is None:
            raise ChannelNotFound

        if not channel["is_private"]:
            return membership or None

        if channel["is_private"] and membership is None:
            raise ChannelMembershipNotFound

        # Workspace owner can do anything cross channels
        if ws_member.role in {"owner"} or membership.role in required_roles:
            return membership

        else:
            raise ChannelMembershipPermissionDenied

    return _dep


CNMemberDep = Annotated[
    Row,
    Depends(get_channel_member_with_roles(required_roles=["owner", "admin", "member"])),
]
CNAdminDep = Annotated[
    Row,
    Depends(get_channel_member_with_roles(required_roles=["owner", "admin"])),
]
CNOwnerDep = Annotated[Row, Depends(get_channel_member_with_roles(required_roles=["owner"]))]
