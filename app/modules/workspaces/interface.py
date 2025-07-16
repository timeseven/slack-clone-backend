from abc import ABC, abstractmethod

from app.modules.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceInvite,
    WorkspaceJoin,
    WorkspaceMembershipRoleUpdate,
    WorkspaceSwitch,
    WorkspaceTransfer,
    WorkspaceUpdate,
)


class IWorkspaceService(ABC):
    @abstractmethod
    async def get_workspaces_by_user(self, user_id: str):
        pass

    @abstractmethod
    async def create_workspace(self, user_id: str, data: WorkspaceCreate):
        pass

    @abstractmethod
    async def get_workspace(self, workspace_id: str, user_id: str):
        pass

    @abstractmethod
    async def get_workspace_membership(self, workspace_id: str, user_id: str):
        pass

    @abstractmethod
    async def update_workspace(self, workspace_id: str, data: WorkspaceUpdate):
        pass

    @abstractmethod
    async def delete_workspace(self, workspace_id: str):
        pass

    @abstractmethod
    async def transfer_ownership(self, workspace_id: str, user_id: str, data: WorkspaceTransfer):
        pass

    @abstractmethod
    async def switch_workspace(self, workspace_id: str, user_id: str, data: WorkspaceSwitch):
        pass

    @abstractmethod
    async def invite_to_workspace(self, workspace_id: str, user_id: str, data: WorkspaceInvite):
        pass

    @abstractmethod
    async def join_workspace(self, workspace_id: str, data: WorkspaceJoin):
        pass

    @abstractmethod
    async def leave_workspace(self, workspace_id: str, user_id: str):
        pass

    @abstractmethod
    async def remove_from_workspace(self, workspace_id: str, user_id: str):
        pass

    @abstractmethod
    async def set_workspace_role(self, workspace_id: str, data: WorkspaceMembershipRoleUpdate):
        pass
