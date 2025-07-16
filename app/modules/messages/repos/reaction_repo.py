from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.messages.models import Reactions


class MessageReactionRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_list(self, workspace_id: str, message_id: str):
        stmt = select(Reactions).where(Reactions.c.workspace_id == workspace_id, Reactions.c.message_id == message_id)
        result = await self.db.execute(stmt)
        return result.fetchall()

    async def get_one(self, workspace_id: str, message_id: str, reaction_id: str):
        stmt = select(Reactions).where(
            Reactions.c.workspace_id == workspace_id,
            Reactions.c.message_id == message_id,
            Reactions.c.id == reaction_id,
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def create(self, workspace_id: str, message_id: str, reaction_id: str, data: dict):
        stmt = (
            insert(Reactions)
            .values(id=reaction_id, workspace_id=workspace_id, message_id=message_id, **data)
            .returning(Reactions)
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def delete(self, workspace_id: str, message_id: str, reaction_id: str):
        stmt = delete(Reactions).where(
            Reactions.c.workspace_id == workspace_id,
            Reactions.c.message_id == message_id,
            Reactions.c.id == reaction_id,
        )
        await self.db.execute(stmt)
