from fastapi import APIRouter, status

from app.core.response import success_response
from app.core.schemas import CustomResponse
from app.modules.channels.deps import (
    ChannelServiceDep,
    CNAdminDep,
    CNMemberDep,
    CNOwnerDep,
)
from app.modules.channels.schemas import (
    ChannelCreate,
    ChannelCreateRead,
    ChannelMemberRead,
    ChannelMembershipRoleUpdate,
    ChannelRead,
    ChannelReadBase,
    ChannelTransfer,
    ChannelUpdate,
)
from app.modules.workspaces.deps import WSMemberDep

channel_router = APIRouter(tags=["channels"])


@channel_router.get("", response_model=CustomResponse[list[ChannelRead]])
async def get_channels(ws_member: WSMemberDep, channel_service: ChannelServiceDep, type: str | None = None):
    channels = await channel_service.get_channels(
        workspace_id=ws_member.workspace_id, user_id=ws_member.user_id, type=type
    )
    return success_response(
        data=[ChannelRead.model_validate(channel, from_attributes=True) for channel in channels],
        message="Channels retrieved successfully",
    )


@channel_router.get("/search", response_model=CustomResponse[list[ChannelRead]])
async def search_channels(ws_member: WSMemberDep, channel_service: ChannelServiceDep, query: str):
    channels = await channel_service.search_channels(
        workspace_id=ws_member.workspace_id, user_id=ws_member.user_id, query=query
    )
    return success_response(
        data=[ChannelReadBase.model_validate(channel, from_attributes=True) for channel in channels],
        message="Channels retrieved successfully",
    )


@channel_router.post("", status_code=status.HTTP_201_CREATED, response_model=CustomResponse[ChannelCreateRead])
async def create_channel(ws_member: WSMemberDep, channel_service: ChannelServiceDep, data: ChannelCreate):
    channel_id = await channel_service.create_channel(
        workspace_id=ws_member.workspace_id, user_id=ws_member.user_id, data=data
    )
    return success_response(
        data={"channel_id": channel_id},
        status_code=status.HTTP_201_CREATED,
        message="Channel created successfully",
    )


@channel_router.get("/{channel_id}", response_model=CustomResponse[ChannelRead])
async def get_channel_by_id(
    ws_member: WSMemberDep, cn_member: CNMemberDep, channel_service: ChannelServiceDep, channel_id: str
):
    workspace_id = cn_member.workspace_id if cn_member else ws_member.workspace_id
    channel_id = cn_member.channel_id if cn_member else channel_id
    user_id = cn_member.user_id if cn_member else ws_member.user_id
    channel = await channel_service.get_channel(workspace_id=workspace_id, channel_id=channel_id, user_id=user_id)
    return success_response(
        data=ChannelRead.model_validate(channel, from_attributes=True),
        message="Channel retrieved successfully",
    )


@channel_router.patch("/{channel_id}", response_model=CustomResponse[ChannelRead])
async def update_channel(cn_admin: CNAdminDep, channel_service: ChannelServiceDep, data: ChannelUpdate):
    channel = await channel_service.update_channel(
        workspace_id=cn_admin.workspace_id, channel_id=cn_admin.channel_id, user_id=cn_admin.user_id, data=data
    )
    return success_response(
        data=ChannelReadBase.model_validate(channel, from_attributes=True),
        message="Channel updated successfully",
    )


@channel_router.delete("/{channel_id}", response_model=CustomResponse)
async def delete_channel(cn_owner: CNOwnerDep, channel_service: ChannelServiceDep):
    await channel_service.delete_channel(workspace_id=cn_owner.workspace_id, channel_id=cn_owner.channel_id)
    return success_response(message="Channel deleted successfully")


@channel_router.patch("/{channel_id}/last-read")
async def update_last_read(cn_member: CNMemberDep, channel_service: ChannelServiceDep):
    await channel_service.update_last_read(
        workspace_id=cn_member.workspace_id, channel_id=cn_member.channel_id, user_id=cn_member.user_id
    )
    return success_response(message="Last read updated successfully")


@channel_router.patch("/{channel_id}/clear-unread")
async def clear_unread_count(cn_member: CNMemberDep, channel_service: ChannelServiceDep):
    await channel_service.update_unread_count(
        workspace_id=cn_member.workspace_id, channel_id=cn_member.channel_id, user_id=cn_member.user_id, unread_count=0
    )
    return success_response(message="Unread count reset successfully")


@channel_router.patch("/{channel_id}/set-role")
async def set_channel_role(cn_owner: CNOwnerDep, channel_service: ChannelServiceDep, data: ChannelMembershipRoleUpdate):
    await channel_service.set_channel_role(
        workspace_id=cn_owner.workspace_id, channel_id=cn_owner.channel_id, data=data
    )
    return success_response(message="Role set successfully")


@channel_router.post("/{channel_id}/transfer")
async def transfer_ownership(cn_owner: CNOwnerDep, channel_service: ChannelServiceDep, data: ChannelTransfer):
    await channel_service.transfer_ownership(
        workspace_id=cn_owner.workspace_id, channel_id=cn_owner.channel_id, user_id=cn_owner.user_id, data=data
    )
    return success_response(message="Channel ownership transferred successfully")


@channel_router.post("/{channel_id}/join")
async def join_channel(ws_member: WSMemberDep, channel_service: ChannelServiceDep, channel_id: str):
    await channel_service.join_channel(
        workspace_id=ws_member.workspace_id, channel_id=channel_id, user_id=ws_member.user_id
    )
    return success_response(message="Joined channel successfully")


@channel_router.post("/{channel_id}/leave")
async def leave_channel(cn_member: CNMemberDep, channel_service: ChannelServiceDep):
    await channel_service.leave_channel(
        workspace_id=cn_member.workspace_id, channel_id=cn_member.channel_id, user_id=cn_member.user_id
    )
    return success_response(message="Left channel successfully")


@channel_router.post("/dms/{user_id}")
async def get_or_create_dm_channel(ws_member: WSMemberDep, channel_service: ChannelServiceDep, user_id: str):
    channel_id = await channel_service.get_or_create_dm_channel(
        workspace_id=ws_member.workspace_id, user_id1=ws_member.user_id, user_id2=user_id
    )
    return success_response(
        data={"channel_id": channel_id},
        status_code=status.HTTP_201_CREATED,
        message="DM channel created successfully",
    )
