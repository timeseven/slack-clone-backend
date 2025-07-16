from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.channels.models import Channel, ChannelMembership


class ChannelRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_list_by_workspace_and_user_with_type(self, workspace_id: str, user_id: str, type: str | None = None):
        stmt = (
            select(Channel)
            .distinct()
            .select_from(
                Channel.join(
                    ChannelMembership,
                    and_(
                        ChannelMembership.c.channel_id == Channel.c.id,
                        ChannelMembership.c.user_id == user_id,
                    ),
                )
            )
            .where(
                Channel.c.workspace_id == workspace_id,
                Channel.c.deleted_at.is_(None),
            )
        )

        if type:
            stmt = stmt.where(Channel.c.type == type)

        result = await self.db.execute(stmt)
        return result.fetchall()

    async def search_list_by_workspace_and_user_with_query(self, workspace_id: str, user_id: str, query: str):
        stmt = (
            select(*Channel.c)
            .distinct()
            .select_from(
                Channel.outerjoin(
                    ChannelMembership,
                    and_(
                        ChannelMembership.c.channel_id == Channel.c.id,
                        ChannelMembership.c.user_id == user_id,
                    ),
                )
            )
            .where(
                Channel.c.workspace_id == workspace_id,
                Channel.c.deleted_at.is_(None),
                or_(
                    ChannelMembership.c.user_id.isnot(None),
                    Channel.c.is_private.is_(False),
                ),
                Channel.c.name.ilike(f"%{query}%"),
            )
        )

        result = await self.db.execute(stmt)
        return result.fetchall()

    async def get_one_by_workspace_and_id(self, workspace_id: str, channel_id: str):
        stmt = select(Channel).where(Channel.c.workspace_id == workspace_id, Channel.c.id == channel_id)
        result = await self.db.execute(stmt)
        return result.first()

    async def create(self, workspace_id: str, channel_id: str, data: dict):
        stmt = insert(Channel).values(id=channel_id, workspace_id=workspace_id, **data)
        await self.db.execute(stmt)

    async def update(self, workspace_id: str, channel_id: str, data: dict):
        stmt = (
            update(Channel)
            .where(Channel.c.workspace_id == workspace_id, Channel.c.id == channel_id)
            .values(**data)
            .returning(Channel)
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def delete(self, workspace_id: str, channel_id: str):
        stmt = delete(Channel).where(Channel.c.workspace_id == workspace_id, Channel.c.id == channel_id)
        await self.db.execute(stmt)
