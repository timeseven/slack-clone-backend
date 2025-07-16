from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.messages.models import Mentions


class MessageMentionRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_list(self, workspace_id: str, message_id: str):
        stmt = select(Mentions).where(Mentions.c.workspace_id == workspace_id, Mentions.c.message_id == message_id)
        result = await self.db.execute(stmt)
        return result.fetchall()

    async def get_one(self, workspace_id: str, message_id: str, mention_id: str):
        stmt = select(Mentions).where(
            Mentions.c.workspace_id == workspace_id,
            Mentions.c.message_id == message_id,
            Mentions.c.id == mention_id,
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def create(self, workspace_id: str, message_id: str, data: dict):
        stmt = insert(Mentions).values(**data)
        await self.db.execute(stmt)

    async def delete(self, workspace_id: str, message_id: str, mention_id: str):
        stmt = delete(Mentions).where(
            Mentions.c.workspace_id == workspace_id,
            Mentions.c.message_id == message_id,
            Mentions.c.id == mention_id,
        )
        await self.db.execute(stmt)
