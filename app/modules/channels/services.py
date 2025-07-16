from asyncio import gather
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.utils import compute_update_fields_from_dict, generate_channel_id, generate_dm_id
from app.modules.channels.exceptions import (
    ChannelMembershipNotFound,
    ChannelMembershipPermissionDenied,
    ChannelNotFound,
)
from app.modules.channels.interface import IChannelService
from app.modules.channels.repos import ChannelMembershipRepo, ChannelRepo
from app.modules.channels.schemas import (
    ChannelCreate,
    ChannelDelete,
    ChannelMemberRoleEnum,
    ChannelMembershipRoleUpdate,
    ChannelTransfer,
    ChannelTypeEnum,
    ChannelUpdate,
)
from app.modules.notifications.realtime.interface import ChannelEventType, IRealtimeNotificationService, UserEventType
from app.modules.users.interface import IUserService
from app.modules.workspaces.interface import IWorkspaceService


class ChannelService(IChannelService):
    def __init__(
        self,
        db: AsyncConnection,
        channel_repo: ChannelRepo,
        channel_membership_repo: ChannelMembershipRepo,
        user_service: IUserService,
        workspace_service: IWorkspaceService,
        real_time_notification_service: IRealtimeNotificationService,
    ):
        self.db = db
        self.channel_repo = channel_repo
        self.channel_membership_repo = channel_membership_repo
        self.user_service = user_service
        self.workspace_service = workspace_service
        self.real_time_notification_service = real_time_notification_service

    async def get_channel_members(self, workspace_id: str, channel_ids: list[str]) -> dict[str, list[dict]]:
        memberships = await self.channel_membership_repo.get_list_by_workspace_and_channels(
            workspace_id=workspace_id, channel_ids=channel_ids
        )

        user_ids = list({m.user_id for m in memberships})
        users = await gather(*[self.user_service.get_user_by_id(uid) for uid in user_ids])
        user_map = {u.id: u for u in users if u}

        memberships_by_channel = defaultdict(list)
        membership_by_channel_user = {}

        for m in memberships:
            memberships_by_channel[m.channel_id].append(m)
            membership_by_channel_user[(m.channel_id, m.user_id)] = m

        role_priority = {"owner": 0, "admin": 1, "member": 2}
        members_by_channel = {}

        for channel_id, memberships in memberships_by_channel.items():
            result = []
            for m in memberships:
                user = user_map.get(m.user_id)
                if not user:
                    continue
                member_data = {
                    **user._mapping,
                    "role": m.role,
                    "is_starred": m.is_starred,
                    "is_muted": m.is_muted,
                    "created_at": m.created_at,
                    "unread_count": m.unread_count,
                    "last_read_at": m.last_read_at,
                }
                result.append(member_data)
            result.sort(key=lambda m: role_priority.get(m["role"], 99))
            members_by_channel[channel_id] = result

        return members_by_channel, membership_by_channel_user

    async def get_channels(self, workspace_id: str, user_id: str, type: str | None = None):
        channels = await self.channel_repo.get_list_by_workspace_and_user_with_type(
            workspace_id=workspace_id, user_id=user_id, type=type
        )
        if not channels:
            return []

        channel_ids = [c.id for c in channels]

        members_by_channel, membership_by_channel_user = await self.get_channel_members(
            workspace_id=workspace_id, channel_ids=channel_ids
        )

        constructed_channels = []
        for channel in channels:
            cid = channel.id
            constructed_channels.append(
                {
                    **dict(channel._mapping),
                    "membership": membership_by_channel_user.get((cid, user_id)),
                    "members": members_by_channel.get(cid, []),
                }
            )

        return constructed_channels

    async def search_channels(self, workspace_id: str, user_id: str, query: str):
        return await self.channel_repo.search_list_by_workspace_and_user_with_query(
            workspace_id=workspace_id, user_id=user_id, query=query
        )

    async def create_channel(self, workspace_id: str, user_id: str, data: ChannelCreate):
        # Create channel
        channel_id = generate_channel_id(channel_type=data.type)

        await self.channel_repo.create(
            workspace_id=workspace_id, channel_id=channel_id, data=data.model_dump(exclude={"template"})
        )

        # Create channel membership
        await self.channel_membership_repo.create(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=user_id,
            data={"role": ChannelMemberRoleEnum.OWNER},
        )

        return channel_id

    async def get_channel(self, workspace_id: str, channel_id: str, user_id: str):
        channel = await self.channel_repo.get_one_by_workspace_and_id(workspace_id=workspace_id, channel_id=channel_id)

        if channel is None:
            raise ChannelNotFound

        members_by_channel, membership_by_channel_user = await self.get_channel_members(workspace_id, [channel_id])

        return {
            **dict(channel._mapping),
            "membership": membership_by_channel_user.get((channel_id, user_id)),
            "members": members_by_channel.get(channel_id, []),
        }

    async def update_channel(
        self, workspace_id: str, channel_id: str, user_id: str, data: ChannelUpdate | ChannelDelete
    ):
        channel = await self.get_channel(workspace_id=workspace_id, channel_id=channel_id, user_id=user_id)

        update_data = compute_update_fields_from_dict(
            old=channel, new_data=data.model_dump(), include_none_fields=["description"]
        )

        if not update_data:
            return channel

        # DMs and Group DMs cannot change is_private
        # Only channels can switch between public and private
        if channel["type"] in [ChannelTypeEnum.DM, ChannelTypeEnum.GROUP_DM] and "is_private" in update_data:
            update_data.pop("is_private")

        channel = await self.channel_repo.update(workspace_id=workspace_id, channel_id=channel_id, data=update_data)

        if channel is None:
            raise ChannelNotFound

        # notify channel members
        await self.real_time_notification_service.send_to_channel(
            channel_id=channel_id,
            event_type=ChannelEventType.CHANNEL_UPDATE,
            data={"workspace_id": workspace_id, "channel_id": channel_id, "channel": update_data},
        )

        return channel

    # Soft delete, change to hard delete if needed
    async def delete_channel(self, workspace_id: str, channel_id: str):
        await self.update_channel(
            workspace_id=workspace_id,
            channel_id=channel_id,
            data=ChannelDelete(deleted_at=datetime.now(tz=timezone.utc)),
        )

    async def update_last_read(self, workspace_id: str, channel_id: str, user_id: str):
        await self.channel_membership_repo.update(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=user_id,
            data={"last_read_at": datetime.now(tz=timezone.utc)},
        )

    async def update_unread_count(
        self, workspace_id: str, channel_id: str, user_id: str, unread_count: int | None = None
    ):
        if unread_count is None:
            current_channel_membership = await self.channel_membership_repo.get_one_by_workspace_channel_user(
                workspace_id=workspace_id, channel_id=channel_id, user_id=user_id
            )
            current_unread_count = current_channel_membership.unread_count if current_channel_membership else 0
            unread_count = current_unread_count + 1

        await self.channel_membership_repo.update(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=user_id,
            data={"unread_count": unread_count},
        )

    async def set_channel_role(self, workspace_id: str, channel_id: str, data: ChannelMembershipRoleUpdate):
        await self.channel_membership_repo.update(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=data.user_id,
            data={"role": data.role},
        )

        # notify channel members
        await self.real_time_notification_service.send_to_user(
            user_id=data.user_id,
            event_type=UserEventType.CHANNEL_ROLE_UPDATE,
            data={"workspace_id": workspace_id, "channel_id": channel_id},
        )

    async def transfer_ownership(self, workspace_id: str, channel_id: str, user_id: str, data: ChannelTransfer):
        # Check if the user is the member of workspace
        new_owner_channel_membership = await self.channel_membership_repo.get_one_by_workspace_channel_user(
            workspace_id=workspace_id, channel_id=channel_id, user_id=data.user_id
        )
        if not new_owner_channel_membership:
            raise ChannelMembershipNotFound("New owner must be a member of the channel")

        # Update the old owner membership of the channel
        await self.channel_membership_repo.update(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=user_id,
            data={"role": ChannelMemberRoleEnum.MEMBER},
        )

        # Update the new owner membership of the channel
        await self.channel_membership_repo.update(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=data.user_id,
            data={"role": ChannelMemberRoleEnum.OWNER},
        )

        # notify channel members
        await self.real_time_notification_service.send_to_channel(
            channel_id=channel_id,
            event_type=ChannelEventType.CHANNEL_TRANSFER,
            data={"workspace_id": workspace_id, "channel_id": channel_id},
        )

    async def join_channel(self, workspace_id: str, channel_id: str, user_id: str):
        await self.channel_membership_repo.create(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=user_id,
            data={"role": ChannelMemberRoleEnum.MEMBER},
        )
        # notify channel members
        await self.real_time_notification_service.send_to_channel(
            channel_id=channel_id,
            event_type=ChannelEventType.CHANNEL_JOIN,
            data={"workspace_id": workspace_id, "channel_id": channel_id},
        )

    async def leave_channel(self, workspace_id: str, channel_id: str, user_id: str):
        channel_membership = await self.channel_membership_repo.get_one_by_workspace_channel_user(
            workspace_id=workspace_id, channel_id=channel_id, user_id=user_id
        )

        if channel_membership is None:
            raise ChannelMembershipNotFound("User is not a member of the channel")

        if channel_membership.role == ChannelMemberRoleEnum.OWNER:
            raise ChannelMembershipPermissionDenied(
                "You are the owner of the channel, transfer ownership before leaving"
            )

        await self.channel_membership_repo.delete(workspace_id=workspace_id, channel_id=channel_id, user_id=user_id)

        # notify channel members
        await self.real_time_notification_service.send_to_channel(
            channel_id=channel_id,
            event_type=ChannelEventType.CHANNEL_LEAVE,
            data={"workspace_id": workspace_id, "channel_id": channel_id},
        )

    async def get_or_create_dm_channel(self, workspace_id: str, user_id1: str, user_id2: str):
        dm_id = generate_dm_id(workspace_id, user_id1, user_id2)
        try:
            await self.get_channel(workspace_id=workspace_id, channel_id=dm_id, user_id=user_id1)
        except ChannelNotFound:
            await self.channel_repo.create(
                workspace_id=workspace_id, channel_id=dm_id, data={"type": ChannelTypeEnum.DM}
            )

            await self.channel_membership_repo.create(
                workspace_id=workspace_id,
                channel_id=dm_id,
                user_id=user_id1,
                data={"role": ChannelMemberRoleEnum.MEMBER},
            )

            # Notify user1
            await self.real_time_notification_service.send_to_user(
                user_id=user_id1,
                event_type=UserEventType.CHANNEL_CREATE,
                data={"workspace_id": workspace_id, "channel_type": "dm"},
            )

            if user_id1 != user_id2:
                await self.channel_membership_repo.create(
                    workspace_id=workspace_id,
                    channel_id=dm_id,
                    user_id=user_id2,
                    data={"role": ChannelMemberRoleEnum.MEMBER},
                )

                # Notify user2
                await self.real_time_notification_service.send_to_user(
                    user_id=user_id2,
                    event_type=UserEventType.CHANNEL_CREATE,
                    data={"workspace_id": workspace_id, "channel_type": "dm"},
                )

        return dm_id
