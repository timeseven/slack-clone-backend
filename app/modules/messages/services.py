from asyncio import gather

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import CursorPagination
from app.core.utils import generate_short_id
from app.modules.channels.interface import IChannelService
from app.modules.messages.exceptions import MessageNotFound, MessagePermissionDenied
from app.modules.messages.interface import IMessageService
from app.modules.messages.repos import MessageMentionRepo, MessageReactionRepo, MessageRepo
from app.modules.messages.schemas import (
    MessageCreate,
    MessageRead,
    MessageUpdate,
    ReactionCreate,
    ReactionRead,
)
from app.modules.notifications.async_tasks.interface import IAsyncNotificationService
from app.modules.notifications.realtime.interface import (
    ChannelEventType,
    IRealtimeNotificationService,
    UserEventType,
)
from app.modules.users.interface import IUserService


class MessageService(IMessageService):
    def __init__(
        self,
        db: AsyncSession,
        message_repo: MessageRepo,
        message_mention_repo: MessageMentionRepo,
        message_reaction_repo: MessageReactionRepo,
        user_service: IUserService,
        channel_service: IChannelService,
        async_notification_service: IAsyncNotificationService,
        real_time_notification_service: IRealtimeNotificationService,
    ):
        self.db = db
        self.message_repo = message_repo
        self.message_mention_repo = message_mention_repo
        self.message_reaction_repo = message_reaction_repo
        self.user_service = user_service
        self.channel_service = channel_service
        self.async_notification_service = async_notification_service
        self.real_time_notification_service = real_time_notification_service

    async def get_message(self, workspace_id: str, message_id: str):
        return await self.message_repo.get_one(workspace_id=workspace_id, message_id=message_id)

    async def get_messages_by_workspace(
        self, workspace_id: str, user_id: str, pagination: CursorPagination | None = None
    ):
        channels = await self.channel_service.get_channels(workspace_id=workspace_id, user_id=user_id)
        channel_ids = [channel["id"] for channel in channels]

        rows = await self.message_repo.get_list_by_workspace_with_pagination(
            workspace_id=workspace_id,
            channel_ids=channel_ids,
            after=pagination.after,
            before=pagination.before,
            limit=pagination.limit,
        )

        message_dict: dict[str, dict] = {}  # message_id -> message obj
        child_buffer: dict[str, list] = {}  # parent_id -> [replies]
        top_level_messages = []

        for row in rows:
            msg = dict(row._mapping)

            # attach reactions, mentions, sender
            msg["reactions"] = await self.message_reaction_repo.get_list(
                workspace_id=workspace_id, message_id=msg["id"]
            )
            msg["mentions"] = await self.message_mention_repo.get_list(workspace_id=workspace_id, message_id=msg["id"])
            msg["sender"] = await self.user_service.get_user_by_id(user_id=msg["sender_id"])
            msg["replies"] = []

            message_dict[msg["id"]] = msg

            if msg["parent_id"]:
                parent_id = msg["parent_id"]
                if parent_id in message_dict:
                    message_dict[parent_id]["replies"].append(msg)
                else:
                    child_buffer.setdefault(parent_id, []).append(msg)
            else:
                top_level_messages.append(msg)

        # attach replies
        for parent_id, children in child_buffer.items():
            if parent_id in message_dict:
                message_dict[parent_id]["replies"].extend(children)

        return top_level_messages

    async def get_messages_by_channel(
        self, workspace_id: str, channel_id: str, pagination: CursorPagination | None = None
    ):
        rows = await self.message_repo.get_list_by_channel_with_pagination(
            workspace_id=workspace_id,
            channel_id=channel_id,
            after=pagination.after,
            before=pagination.before,
            limit=pagination.limit,
        )
        top_messages = [dict(row._mapping) for row in rows]

        if not top_messages:
            return []

        top_message_ids = [msg["id"] for msg in top_messages]

        # Step 2: Lookup replies of top-level message
        reply_rows = await self.message_repo.get_list_with_parent_id(
            workspace_id=workspace_id,
            channel_id=channel_id,
            parent_ids=top_message_ids,
        )
        replies = [dict(row._mapping) for row in reply_rows]

        # Step 3: enrich
        async def enrich(msg):
            msg["reactions"] = await self.message_reaction_repo.get_list(
                workspace_id=workspace_id, message_id=msg["id"]
            )
            msg["mentions"] = await self.message_mention_repo.get_list(workspace_id=workspace_id, message_id=msg["id"])
            msg["sender"] = await self.user_service.get_user_by_id(msg["sender_id"])
            msg["replies"] = []
            return msg

        top_messages = await gather(*(enrich(msg) for msg in top_messages))
        replies = await gather(*(enrich(msg) for msg in replies))

        # Step 4: attach replies
        message_dict = {msg["id"]: msg for msg in top_messages}
        for reply in replies:
            parent_id = reply["parent_id"]
            if parent_id in message_dict:
                message_dict[parent_id]["replies"].append(reply)

        return top_messages

    async def create_message(self, workspace_id: str, channel_id: str, user_id: str, data: MessageCreate):
        message_id = generate_short_id(prefix="M")

        message = await self.message_repo.create(
            workspace_id=workspace_id,
            channel_id=channel_id,
            message_id=message_id,
            data={
                "sender_id": user_id,
                "content": data.content,
                "parent_id": data.parent_id,
                "message_type": data.message_type,
            },
        )
        message = dict(message._mapping)

        user_row = await self.user_service.get_user_by_id(message["sender_id"])
        message["sender"] = dict(user_row._mapping)
        message["reactions"] = []
        message["mentions"] = []
        message["replies"] = []

        # Get all channel members
        members_by_channel, _ = await self.channel_service.get_channel_members(
            workspace_id=workspace_id, channel_ids=[channel_id]
        )
        all_channel_members = members_by_channel.get(channel_id, [])
        all_channel_member_ids = {member["id"] for member in all_channel_members}

        # Get online users in channel
        online_channel_member_ids = self.real_time_notification_service.get_online_users_in_channel(
            channel_id=channel_id
        )

        offline_or_left_member_ids = all_channel_member_ids - online_channel_member_ids

        # Notify all online users in channel
        await self.real_time_notification_service.send_to_channel(
            channel_id=channel_id,
            event_type=ChannelEventType.MESSAGE_CREATE,
            data={
                "workspace_id": workspace_id,
                "channel_id": channel_id,
                "message": MessageRead.model_validate(message, from_attributes=True).serializable_dict(),
            },
        )

        # Update unread count for offline or left users and notify them
        if offline_or_left_member_ids:
            await gather(
                *[
                    self.channel_service.update_unread_count(
                        workspace_id=workspace_id,
                        channel_id=channel_id,
                        user_id=uid,
                    )
                    for uid in offline_or_left_member_ids
                ]
            )
            await self.async_notification_service.notify_users_event_type(
                event_type=UserEventType.MESSAGE_UNREAD,
                user_ids=offline_or_left_member_ids,
                data={
                    "workspace_id": workspace_id,
                    "channel_id": channel_id,
                },
            )

        return message_id

    async def update_message(
        self, workspace_id: str, channel_id: str, message_id: str, user_id: str, data: MessageUpdate
    ):
        existing_message = await self.get_message(workspace_id=workspace_id, message_id=message_id)
        if not existing_message:
            raise MessageNotFound

        if existing_message["sender_id"] != user_id:
            raise MessagePermissionDenied(detail="Only message sender can update message")

        message = await self.message_repo.update(
            workspace_id=workspace_id,
            channel_id=channel_id,
            message_id=message_id,
            data={
                "content": data.content,
            },
        )
        message = dict(message._mapping)

        user_row = await self.user_service.get_user_by_id(message["sender_id"])
        message["sender"] = dict(user_row._mapping)
        message["reactions"] = []
        message["mentions"] = []
        message["replies"] = []

        return message

    async def create_reaction(
        self, workspace_id: str, channel_id: str, message_id: str, user_id: str, data: ReactionCreate
    ):
        reaction_id = generate_short_id(prefix="MR")
        print("xxxxxxxxxxxx", reaction_id)
        reaction = await self.message_reaction_repo.create(
            workspace_id=workspace_id,
            message_id=message_id,
            reaction_id=reaction_id,
            data={
                "emoji": data.emoji,
                "sender_id": user_id,
            },
        )

        # Send realtime notification to the channels
        await self.real_time_notification_service.send_to_channel(
            channel_id=channel_id,
            event_type=ChannelEventType.REACTION_CREATE,
            data={
                "workspace_id": workspace_id,
                "channel_id": channel_id,
                "message_id": message_id,
                "reaction": ReactionRead.model_validate(reaction, from_attributes=True).serializable_dict(),
            },
        )

        return reaction_id

    async def delete_reaction(
        self, workspace_id: str, channel_id: str, message_id: str, user_id: str, reaction_id: str
    ):
        await self.message_reaction_repo.delete(
            workspace_id=workspace_id, message_id=message_id, reaction_id=reaction_id
        )

        await self.real_time_notification_service.send_to_channel(
            channel_id=channel_id,
            event_type=ChannelEventType.REACTION_DELETE,
            data={
                "workspace_id": workspace_id,
                "channel_id": channel_id,
                "message_id": message_id,
                "reaction_id": reaction_id,
            },
        )
