from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.workspaces.models import WorkspaceMembership
from app.modules.workspaces.schemas import WorkspaceMemberRoleEnum


class WorkspaceMembershipRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_list_by_user(self, user_id: str):
        stmt = select(WorkspaceMembership).where(WorkspaceMembership.c.user_id == user_id)
        return (await self.db.execute(stmt)).fetchall()

    async def count_owned_by_user(self, user_id: str):
        stmt = select(WorkspaceMembership).where(
            WorkspaceMembership.c.user_id == user_id,
            WorkspaceMembership.c.role == WorkspaceMemberRoleEnum.OWNER,
        )
        return len((await self.db.execute(stmt)).fetchall())

    async def get_list_by_workspaces(self, workspace_ids: list[str]):
        stmt = select(WorkspaceMembership).where(WorkspaceMembership.c.workspace_id.in_(workspace_ids))
        return (await self.db.execute(stmt)).fetchall()

    async def get_one_by_workspace(self, workspace_id: str):
        stmt = select(WorkspaceMembership).where(WorkspaceMembership.c.workspace_id == workspace_id)
        return (await self.db.execute(stmt)).fetchall()

    async def get_active_one_by_user(self, user_id: str):
        stmt = select(WorkspaceMembership).where(
            WorkspaceMembership.c.user_id == user_id,
            WorkspaceMembership.c.is_active,
        )
        return (await self.db.execute(stmt)).first()

    async def get_one_by_workspace_and_user(self, workspace_id: str, user_id: str):
        stmt = select(WorkspaceMembership).where(
            WorkspaceMembership.c.workspace_id == workspace_id,
            WorkspaceMembership.c.user_id == user_id,
        )
        return (await self.db.execute(stmt)).first()

    async def create(self, workspace_id: str, user_id: str, data: dict):
        stmt = insert(WorkspaceMembership).values(workspace_id=workspace_id, user_id=user_id, **data)
        await self.db.execute(stmt)

    async def update(self, workspace_id: str, user_id: str, data: dict):
        stmt = (
            update(WorkspaceMembership)
            .where(
                WorkspaceMembership.c.workspace_id == workspace_id,
                WorkspaceMembership.c.user_id == user_id,
            )
            .values(**data)
            .returning(WorkspaceMembership)
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def delete(self, workspace_id: str, user_id: str):
        stmt = delete(WorkspaceMembership).where(
            WorkspaceMembership.c.workspace_id == workspace_id,
            WorkspaceMembership.c.user_id == user_id,
        )
        await self.db.execute(stmt)
