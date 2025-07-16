from datetime import datetime

from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.messages.models import Message


class MessageRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_one(self, workspace_id: str, message_id: str):
        stmt = select(Message).where(Message.c.workspace_id == workspace_id, Message.c.id == message_id)
        result = await self.db.execute(stmt)
        return result.first()

    async def get_list_by_workspace_with_pagination(
        self,
        workspace_id: str,
        channel_ids: list[str],
        after: datetime | None = None,
        before: datetime | None = None,
        limit: int | None = None,
    ):
        stmt = (
            select(Message)
            .where(Message.c.workspace_id == workspace_id, Message.c.channel_id.in_(channel_ids))
            .order_by(Message.c.created_at.desc())
        )

        if after:
            stmt = stmt.where(Message.c.created_at > after)

        if before:
            stmt = stmt.where(Message.c.created_at < before)

        if limit:
            stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        return result.fetchall()

    async def get_list_by_channel_with_pagination(
        self,
        workspace_id: str,
        channel_id: str,
        after: datetime | None = None,
        before: datetime | None = None,
        limit: int | None = None,
    ):
        stmt = (
            select(Message)
            .where(
                Message.c.workspace_id == workspace_id,
                Message.c.channel_id == channel_id,
                Message.c.parent_id.is_(None),
            )
            .order_by(Message.c.created_at.desc())
        )

        if after:
            stmt = stmt.where(Message.c.created_at > after)

        if before:
            stmt = stmt.where(Message.c.created_at < before)

        if limit:
            stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        return result.fetchall()

    async def get_list_with_parent_id(self, workspace_id: str, channel_id: str, parent_ids: list[str]):
        stmt = (
            select(Message)
            .where(
                Message.c.workspace_id == workspace_id,
                Message.c.channel_id == channel_id,
                Message.c.parent_id.in_(parent_ids),
            )
            .order_by(Message.c.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.fetchall()

    async def create(self, workspace_id: str, channel_id: str, message_id: str, data: dict):
        stmt = (
            insert(Message)
            .values(id=message_id, workspace_id=workspace_id, channel_id=channel_id, **data)
            .returning(Message)
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def update(self, workspace_id: str, channel_id: str, message_id: str, data: dict):
        stmt = (
            update(Message)
            .where(
                Message.c.workspace_id == workspace_id, Message.c.channel_id == channel_id, Message.c.id == message_id
            )
            .values(**data)
            .returning(Message)
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def delete(self, workspace_id: str, channel_id: str, message_id: str):
        stmt = delete(Message).where(
            Message.c.workspace_id == workspace_id, Message.c.channel_id == channel_id, Message.c.id == message_id
        )
        await self.db.execute(stmt)
