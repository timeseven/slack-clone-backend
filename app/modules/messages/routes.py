from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.response import success_response
from app.core.schemas import CursorPagination, CustomResponse
from app.modules.channels.deps import CNMemberDep
from app.modules.messages.deps import MessageServiceDep
from app.modules.messages.schemas import (
    MessageCreate,
    MessageCreateRead,
    MessageRead,
    MessageUpdate,
    ReactionCreate,
    ReactionCreateRead,
)
from app.modules.workspaces.deps import WSMemberDep

message_router = APIRouter(tags=["messages"])


@message_router.get("/messages", response_model=CustomResponse[MessageRead])
async def get_messages_by_workspace(
    ws_member: WSMemberDep,
    message_service: MessageServiceDep,
    pagination: Annotated[CursorPagination, Query()],
):
    messages = await message_service.get_messages_by_workspace(
        workspace_id=ws_member.workspace_id, user_id=ws_member.user_id, pagination=pagination
    )
    return success_response(
        data=[MessageRead.model_validate(message, from_attributes=True) for message in messages],
        message="Messages retrieved successfully",
    )


@message_router.get("/channels/{channel_id}/messages", response_model=CustomResponse[list[MessageRead]])
async def get_messages_by_channel(
    ws_member: WSMemberDep,
    message_service: MessageServiceDep,
    channel_id: str,
    pagination: Annotated[CursorPagination, Query()],
):
    messages = await message_service.get_messages_by_channel(
        workspace_id=ws_member.workspace_id, channel_id=channel_id, pagination=pagination
    )
    return success_response(
        data=[MessageRead.model_validate(message, from_attributes=True) for message in messages],
        message="Messages retrieved successfully",
    )


@message_router.post(
    "/channels/{channel_id}/messages",
    status_code=status.HTTP_201_CREATED,
    response_model=CustomResponse[MessageCreateRead],
)
async def create_message(cn_member: CNMemberDep, message_service: MessageServiceDep, data: MessageCreate):
    message_id = await message_service.create_message(
        workspace_id=cn_member.workspace_id, channel_id=cn_member.channel_id, user_id=cn_member.user_id, data=data
    )
    return success_response(
        status_code=status.HTTP_201_CREATED,
        data={"message_id": message_id},
        message="Message created successfully",
    )


@message_router.patch("/channels/{channel_id}/messages/{message_id}")
async def update_message(
    cn_member: CNMemberDep, message_service: MessageServiceDep, message_id: str, data: MessageUpdate
):
    message = await message_service.update_message(
        workspace_id=cn_member.workspace_id,
        channel_id=cn_member.channel_id,
        message_id=message_id,
        user_id=cn_member.user_id,
        data=data,
    )
    return success_response(
        data=MessageRead.model_validate(message, from_attributes=True),
        message="Message updated successfully",
    )


@message_router.delete("/channels/{channel_id}/messages/{message_id}")
async def delete_message():
    return


@message_router.post(
    "/channels/{channel_id}/messages/{message_id}/reactions",
    status_code=status.HTTP_201_CREATED,
    response_model=CustomResponse[ReactionCreateRead],
)
async def create_reaction(
    cn_member: CNMemberDep, message_service: MessageServiceDep, message_id: str, data: ReactionCreate
):
    reaction_id = await message_service.create_reaction(
        workspace_id=cn_member.workspace_id,
        channel_id=cn_member.channel_id,
        message_id=message_id,
        user_id=cn_member.user_id,
        data=data,
    )
    return success_response(
        status_code=status.HTTP_201_CREATED,
        data={"reaction_id": reaction_id},
        message="Reaction created successfully",
    )


@message_router.delete(
    "/channels/{channel_id}/messages/{message_id}/reactions/{reaction_id}", response_model=CustomResponse
)
async def delete_reaction(
    cn_member: CNMemberDep, message_service: MessageServiceDep, message_id: str, reaction_id: str
):
    await message_service.delete_reaction(
        workspace_id=cn_member.workspace_id,
        channel_id=cn_member.channel_id,
        message_id=message_id,
        user_id=cn_member.user_id,
        reaction_id=reaction_id,
    )
    return success_response(message="Reaction deleted successfully")


@message_router.get("/mentions")
async def get_mentions_by_workspace():
    return


@message_router.post("/channels/{channel_id}/messages/{message_id}/mentions")
async def create_mention():
    return
