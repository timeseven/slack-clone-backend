from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.workspaces.models import WorkspaceInvitation


class WorkspaceInvitationRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_one_by_id(self, id: str):
        stmt = select(WorkspaceInvitation).where(WorkspaceInvitation.c.id == id)
        return (await self.db.execute(stmt)).first()

    async def get_list_by_workspace_and_invitees(self, workspace_id: str, invitee_ids: list[str]):
        stmt = select(WorkspaceInvitation).where(
            WorkspaceInvitation.c.workspace_id == workspace_id,
            WorkspaceInvitation.c.invitee_id.in_(invitee_ids),
        )
        return (await self.db.execute(stmt)).fetchall()

    async def create(self, invitation_id: str, data: dict):
        stmt = insert(WorkspaceInvitation).values(id=invitation_id, **data)
        await self.db.execute(stmt)

    async def update(self, workspace_invitation_id: str, data: dict):
        stmt = (
            update(WorkspaceInvitation)
            .where(WorkspaceInvitation.c.id == workspace_invitation_id)
            .values(**data)
            .returning(WorkspaceInvitation)
        )
        result = await self.db.execute(stmt)
        return result.first()

    async def delete(self, workspace_invitation_id: str):
        stmt = delete(WorkspaceInvitation).where(WorkspaceInvitation.c.id == workspace_invitation_id)
        await self.db.execute(stmt)
