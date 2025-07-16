from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.channels.models import ChannelMembership


class ChannelMembershipRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_list_by_workspace_and_channel(self, workspace_id: str, channel_id: str):
        stmt = select(ChannelMembership).where(
            ChannelMembership.c.workspace_id == workspace_id,
            ChannelMembership.c.channel_id == channel_id,
        )
        result = await self.db.execute(stmt)
        return result.fetchall()

    async def get_list_by_workspace_and_channels(self, workspace_id: str, channel_ids: list[str]):
        stmt = select(ChannelMembership).where(
            ChannelMembership.c.workspace_id == workspace_id,
            ChannelMembership.c.channel_id.in_(channel_ids),
        )
        result = await self.db.execute(stmt)
        return result.fetchall()

    async def get_one_by_workspace_channel_user(self, workspace_id: str, channel_id: str, user_id: str):
        stmt = select(ChannelMembership).where(
            ChannelMembership.c.workspace_id == workspace_id,
            ChannelMembership.c.channel_id == channel_id,
            ChannelMembership.c.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def create(self, workspace_id: str, channel_id: str, user_id: str, data: dict):
        stmt = insert(ChannelMembership).values(
            workspace_id=workspace_id, channel_id=channel_id, user_id=user_id, **data
        )
        await self.db.execute(stmt)

    async def update(self, workspace_id: str, channel_id: str, user_id: str, data: dict):
        stmt = (
            update(ChannelMembership)
            .where(
                ChannelMembership.c.workspace_id == workspace_id,
                ChannelMembership.c.channel_id == channel_id,
                ChannelMembership.c.user_id == user_id,
            )
            .values(**data)
        )
        await self.db.execute(stmt)

    async def delete(self, workspace_id: str, channel_id: str, user_id: str):
        stmt = delete(ChannelMembership).where(
            ChannelMembership.c.workspace_id == workspace_id,
            ChannelMembership.c.channel_id == channel_id,
            ChannelMembership.c.user_id == user_id,
        )
        await self.db.execute(stmt)
