from fastapi import APIRouter, status

from app.core.response import success_response
from app.core.schemas import CustomResponse
from app.modules.auth.deps import UserDep
from app.modules.workspaces.deps import (
    WorkspaceServiceDep,
    WSAdminDep,
    WSMemberDep,
    WSOwnerDep,
)
from app.modules.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceCreateRead,
    WorkspaceDetailRead,
    WorkspaceInvite,
    WorkspaceJoin,
    WorkspaceMembershipRoleUpdate,
    WorkspaceRead,
    WorkspaceReadBase,
    WorkspaceSwitch,
    WorkspaceTransfer,
    WorkspaceUpdate,
)

workspace_router = APIRouter(tags=["workspaces"])


@workspace_router.get("", response_model=CustomResponse[list[WorkspaceRead]])
async def get_workspace_by_user(
    user: UserDep,
    workspace_service: WorkspaceServiceDep,
):
    workspaces = await workspace_service.get_workspaces_by_user(user_id=user.id)
    return success_response(
        data=[WorkspaceRead.model_validate(workspace, from_attributes=True) for workspace in workspaces],
        message="Workspaces retrieved successfully",
    )


@workspace_router.post("", status_code=status.HTTP_201_CREATED, response_model=CustomResponse[WorkspaceCreateRead])
async def create_workspace(
    user: UserDep,
    workspace_service: WorkspaceServiceDep,
    data: WorkspaceCreate,
):
    workspace_id = await workspace_service.create_workspace(user_id=user.id, data=data)
    return success_response(
        data={"workspace_id": workspace_id},
        status_code=status.HTTP_201_CREATED,
        message="Workspace created successfully",
    )


@workspace_router.patch("/choose", response_model=CustomResponse)
async def choose_workspace(
    user: UserDep,
    workspace_service: WorkspaceServiceDep,
    data: WorkspaceSwitch,
):
    await workspace_service.switch_workspace(user_id=user.id, data=data)
    return success_response(message="Workspace chosen successfully")


@workspace_router.get("/{workspace_id}", response_model=CustomResponse[WorkspaceDetailRead])
async def get_workspace(
    ws_member: WSMemberDep,
    workspace_service: WorkspaceServiceDep,
):
    worksapce = await workspace_service.get_workspace(workspace_id=ws_member.workspace_id, user_id=ws_member.user_id)
    return success_response(
        data=WorkspaceDetailRead.model_validate(worksapce, from_attributes=True),
        message="Workspace retrieved successfully",
    )


@workspace_router.patch("/{workspace_id}", response_model=CustomResponse[WorkspaceReadBase])
async def update_workspace(
    ws_admin: WSAdminDep,
    workspace_service: WorkspaceServiceDep,
    data: WorkspaceUpdate,
):
    workspace = await workspace_service.update_workspace(workspace_id=ws_admin.workspace_id, data=data)
    return success_response(
        data=WorkspaceReadBase.model_validate(workspace, from_attributes=True),
        message="Workspace updated successfully",
    )


@workspace_router.delete("/{workspace_id}", response_model=CustomResponse)
async def delete_workspace(
    ws_owner: WSOwnerDep,
    workspace_service: WorkspaceServiceDep,
):
    await workspace_service.delete_workspace(workspace_id=ws_owner.workspace_id)
    return success_response(message="Workspace deleted successfully")


@workspace_router.patch("/{workspace_id}/transfer", response_model=CustomResponse)
async def transfer_ownership(
    ws_owner: WSOwnerDep,
    workspace_service: WorkspaceServiceDep,
    data: WorkspaceTransfer,
):
    await workspace_service.transfer_ownership(workspace_id=ws_owner.workspace_id, user_id=ws_owner.user_id, data=data)
    return success_response(message="Workspace ownership transferred successfully")


@workspace_router.patch("/{workspace_id}/switch", response_model=CustomResponse)
async def switch_workspace(
    ws_member: WSMemberDep,
    workspace_service: WorkspaceServiceDep,
    data: WorkspaceSwitch,
):
    await workspace_service.switch_workspace(workspace_id=ws_member.workspace_id, user_id=ws_member.user_id, data=data)
    return success_response(message="Workspace switched successfully")


@workspace_router.post(
    "/{workspace_id}/invite",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=CustomResponse,
)
async def invite_to_workspace(
    ws_admin: WSAdminDep,
    workspace_service: WorkspaceServiceDep,
    data: WorkspaceInvite,
):
    await workspace_service.invite_to_workspace(workspace_id=ws_admin.workspace_id, user_id=ws_admin.user_id, data=data)
    return success_response(
        status_code=status.HTTP_202_ACCEPTED,
        message="Workspace invitation sent successfully",
    )


@workspace_router.post("/{workspace_id}/join", response_model=CustomResponse)
async def join_workspace(
    workspace_service: WorkspaceServiceDep,
    workspace_id: str,
    data: WorkspaceJoin,
):
    await workspace_service.join_workspace(workspace_id=workspace_id, data=data)
    return success_response(message="Workspace joined successfully")


@workspace_router.patch("/{workspace_id}/leave", response_model=CustomResponse)
async def leave_workspace(
    ws_member: WSMemberDep,
    workspace_service: WorkspaceServiceDep,
):
    await workspace_service.leave_workspace(workspace_id=ws_member.workspace_id, user_id=ws_member.user_id)
    return success_response(message="Workspace left successfully")


@workspace_router.patch("/{workspace_id}/remove/{user_id}", response_model=CustomResponse)
async def remove_from_workspace(
    ws_owner: WSOwnerDep,
    workspace_service: WorkspaceServiceDep,
    user_id: str,
):
    await workspace_service.remove_from_workspace(workspace_id=ws_owner.workspace_id, user_id=user_id)
    return success_response(message="Workspace left successfully")


@workspace_router.patch("/{workspace_id}/set-role", response_model=CustomResponse)
async def set_workspace_role(
    ws_owner: WSOwnerDep, workspace_service: WorkspaceServiceDep, data: WorkspaceMembershipRoleUpdate
):
    await workspace_service.set_workspace_role(workspace_id=ws_owner.workspace_id, data=data)
    return success_response(message="Role set successfully")
