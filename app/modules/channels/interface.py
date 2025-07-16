from abc import ABC, abstractmethod

from app.modules.channels.schemas import (
    ChannelCreate,
    ChannelDelete,
    ChannelMembershipRoleUpdate,
    ChannelTransfer,
    ChannelUpdate,
)


class IChannelService(ABC):
    @abstractmethod
    async def get_or_create_dm_channel(self, workspace_id: str, user_id1: str, user_id2: str):
        pass

    @abstractmethod
    async def get_channels(self, workspace_id: str, user_id: str, type: str | None = None):
        pass

    @abstractmethod
    async def get_channel_members(self, workspace_id: str, channel_ids: list[str]):
        pass

    @abstractmethod
    async def search_channels(self, workspace_id: str, user_id: str, query: str):
        pass

    @abstractmethod
    async def create_channel(self, workspace_id: str, user_id: str, data: ChannelCreate):
        pass

    @abstractmethod
    async def get_channel(self, workspace_id: str, channel_id: str, user_id: str):
        pass

    @abstractmethod
    async def update_channel(
        self, workspace_id: str, channel_id: str, user_id: str, data: ChannelUpdate | ChannelDelete
    ):
        pass

    @abstractmethod
    async def delete_channel(self, workspace_id: str, channel_id: str):
        pass

    @abstractmethod
    async def update_last_read(self, workspace_id: str, channel_id: str, user_id: str):
        pass

    @abstractmethod
    async def update_unread_count(
        self, workspace_id: str, channel_id: str, user_id: str, unread_count: int | None = None
    ):
        pass

    @abstractmethod
    async def set_channel_role(self, workspace_id: str, channel_id: str, data: ChannelMembershipRoleUpdate):
        pass

    @abstractmethod
    async def transfer_ownership(self, workspace_id: str, channel_id: str, user_id: str, data: ChannelTransfer):
        pass

    @abstractmethod
    async def join_channel(self, workspace_id: str, channel_id: str, user_id: str):
        pass

    @abstractmethod
    async def leave_channel(self, workspace_id: str, channel_id: str, user_id: str):
        pass
