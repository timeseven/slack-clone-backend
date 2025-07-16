# Realtime notification module interface exposing services
# Used to decouple implementation and support future extensions.

from abc import ABC, abstractmethod
from typing import Any

from app.modules.notifications.realtime.event_type import (  # noqa F401
    ChannelEventType,
    UserEventType,
    WorkspaceEventType,
)


class IRealtimeNotificationService(ABC):
    @abstractmethod
    def get_online_users_in_channel(self, channel_id: str):
        pass

    @abstractmethod
    async def send_to_user(self, user_id: str, event_type: str, data: dict[str, Any]):
        pass

    @abstractmethod
    async def send_to_workspace(self, workspace_id: str, event_type: str, data: dict[str, Any]):
        pass

    @abstractmethod
    async def send_to_channel(self, channel_id: str, event_type: str, data: dict[str, Any]):
        pass

    @abstractmethod
    async def broadcast(self, event_type: str, data: dict[str, Any]):
        pass
