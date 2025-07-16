from abc import ABC, abstractmethod

from app.core.schemas import CursorPagination
from app.modules.messages.schemas import MessageCreate, MessageUpdate, ReactionCreate


class IMessageService(ABC):
    @abstractmethod
    async def get_messages_by_workspace(self, workspace_id: str, pagination: CursorPagination):
        pass

    @abstractmethod
    async def get_messages_by_channel(
        self, workspace_id: str, channel_id: str, pagination: CursorPagination | None = None
    ):
        pass

    @abstractmethod
    async def create_message(self, workspace_id: str, channel_id: str, user_id: str, data: MessageCreate):
        pass

    @abstractmethod
    async def update_message(
        self, workspace_id: str, channel_id: str, message_id: str, user_id: str, data: MessageUpdate
    ):
        pass

    @abstractmethod
    async def create_reaction(
        self, workspace_id: str, channel_id: str, message_id: str, user_id: str, data: ReactionCreate
    ):
        pass

    @abstractmethod
    async def delete_reaction(
        self, workspace_id: str, channel_id: str, message_id: str, user_id: str, reaction_id: str
    ):
        pass
