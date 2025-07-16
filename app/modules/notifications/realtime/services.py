from typing import Any

from app.modules.notifications.realtime.interface import IRealtimeNotificationService
from app.modules.notifications.realtime.socketio_manager import SocketIOManager


class RealtimeNotificationService(IRealtimeNotificationService):
    def __init__(self, socketio_manager: SocketIOManager):
        self._socketio_manager = socketio_manager

    async def send_to_user(self, user_id: str, event_type: str, data: dict[str, Any]):
        await self._socketio_manager.emit_to_room(f"user_{user_id}", event_type, data)

    async def send_to_workspace(self, workspace_id: str, event_type: str, data: dict[str, Any]):
        print("send_to_workspace", workspace_id, event_type, data)
        await self._socketio_manager.emit_to_room(f"workspace_{workspace_id}", event_type, data)

    async def send_to_channel(self, channel_id: str, event_type: str, data: dict[str, Any]):
        await self._socketio_manager.emit_to_room(f"channel_{channel_id}", event_type, data)

    async def broadcast(self, event_type: str, data: dict[str, Any]):
        await self._socketio_manager.broadcast(event_type, data)

    def get_online_users_in_channel(self, channel_id: str) -> set[str]:
        return self._socketio_manager.get_online_users_in_channel(channel_id)
