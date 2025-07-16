from typing import Annotated, Callable

from fastapi import Depends
from sqlalchemy import Row

from app.core.deps import DBConnDep
from app.modules.auth.deps import UserDep
from app.modules.files.deps import FileServiceDep
from app.modules.notifications.async_tasks.deps import AsyncNotificationServiceDep
from app.modules.notifications.realtime.deps import RealTimeNotificationServiceDep
from app.modules.users.deps import UserServiceDep
from app.modules.workspaces.exceptions import (
    WSBadRequest,
    WSMembershipNotFound,
    WSMembershipPermissionDenied,
    WSNotFound,
)
from app.modules.workspaces.interface import IWorkspaceService
from app.modules.workspaces.repos import WorkspaceInvitationRepo, WorkspaceMembershipRepo, WorkspaceRepo
from app.modules.workspaces.services import WorkspaceService


async def get_workspace_repo(db: DBConnDep):
    return WorkspaceRepo(db)


async def get_workspace_membership_repo(db: DBConnDep):
    return WorkspaceMembershipRepo(db)


async def get_workspace_invitation_repo(db: DBConnDep):
    return WorkspaceInvitationRepo(db)


WorkspaceRepoDep = Annotated[WorkspaceRepo, Depends(get_workspace_repo)]
WorkspaceMembershipRepoDep = Annotated[WorkspaceMembershipRepo, Depends(get_workspace_membership_repo)]
WorkspaceInvitationRepoDep = Annotated[WorkspaceInvitationRepo, Depends(get_workspace_invitation_repo)]


async def get_workspace_service(
    workspace_repo: WorkspaceRepoDep,
    workspace_membership_repo: WorkspaceMembershipRepoDep,
    workspace_invitation_repo: WorkspaceInvitationRepoDep,
    user_service: UserServiceDep,
    async_notification_service: AsyncNotificationServiceDep,
    real_time_notification_service: RealTimeNotificationServiceDep,
    file_service: FileServiceDep,
) -> IWorkspaceService:
    return WorkspaceService(
        workspace_repo=workspace_repo,
        workspace_membership_repo=workspace_membership_repo,
        workspace_invitation_repo=workspace_invitation_repo,
        user_service=user_service,
        async_notification_service=async_notification_service,
        real_time_notification_service=real_time_notification_service,
        file_service=file_service,
    )


WorkspaceServiceDep = Annotated[IWorkspaceService, Depends(get_workspace_service)]

VALID_ROLES = {"owner", "admin", "member"}


def get_ws_member_with_roles(required_roles: list[str]) -> Callable:
    assert all(role in VALID_ROLES for role in required_roles), "Invalid role in required_roles"

    async def _dep(
        user: UserDep,
        workspace_id: str,
        workspace_service: WorkspaceServiceDep,
    ):
        if workspace_id is None:
            raise WSNotFound

        workspace_membership = await workspace_service.get_workspace_membership(
            workspace_id=workspace_id, user_id=user.id
        )
        print("workspace_membership", workspace_membership)
        if workspace_membership is None:
            raise WSMembershipNotFound

        if workspace_membership.is_active is False:
            raise WSBadRequest(detail="Switch to this workspace to perform this action.")

        if workspace_membership.role not in required_roles:
            raise WSMembershipPermissionDenied(detail="You don't have permission to perform this action.")

        return workspace_membership

    return _dep


WSMemberDep = Annotated[
    Row,
    Depends(get_ws_member_with_roles(["admin", "owner", "member"])),
]
WSAdminDep = Annotated[Row, Depends(get_ws_member_with_roles(["admin", "owner"]))]
WSOwnerDep = Annotated[Row, Depends(get_ws_member_with_roles(["owner"]))]
