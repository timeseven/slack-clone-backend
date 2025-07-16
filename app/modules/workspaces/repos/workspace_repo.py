from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.workspaces.models import Workspace


class WorkspaceRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    # Get all workspaces including soft deleted ones
    async def get_one_by_name(self, name: str):
        stmt = select(Workspace).where(Workspace.c.name == name)
        return (await self.db.execute(stmt)).first()

    async def get_one_by_id(self, workspace_id: str):
        stmt = select(Workspace).where(Workspace.c.id == workspace_id, Workspace.c.deleted_at.is_(None))
        return (await self.db.execute(stmt)).first()

    async def get_list_by_ids(self, workspace_ids: list[str]):
        stmt = select(Workspace).where(Workspace.c.id.in_(workspace_ids), Workspace.c.deleted_at.is_(None))
        return (await self.db.execute(stmt)).fetchall()

    async def create(self, workspace_id: str, data: dict):
        stmt = insert(Workspace).values(id=workspace_id, **data)
        await self.db.execute(stmt)

    async def update(self, workspace_id: str, data: dict):
        stmt = (
            update(Workspace)
            .where(Workspace.c.id == workspace_id)
            .where(Workspace.c.deleted_at.is_(None))
            .values(**data)
            .returning(Workspace)
        )

        result = await self.db.execute(stmt)
        return result.first()

    # Hard delete
    async def delete(self, workspace_id: str):
        stmt = delete(Workspace).where(Workspace.c.id == workspace_id)
        await self.db.execute(stmt)
