from typing import Any

from loguru import logger

from app.modules.notifications.realtime.socketio_app import sio


class SocketIOManager:
    def __init__(self):
        # Maintain a mapping from sid to user_id, user_id to sids and channel_subscriptions
        self._sid_to_user_id: dict[str, str] = {}
        self._user_id_to_sids: dict[str, set[str]] = {}
        self._channel_subscriptions: dict[str, set[str]] = {}

    def setup_event_handlers(self):
        """Set up connection and custom event handlers for the Socket.IO server."""

        @sio.event
        async def connect(sid, environ, auth):
            """
            Handle a new Socket.IO connection.
            **No rooms are joined automatically.** Clients must send a 'join_user_room' event.
            """
            user_id = auth.get("user_id") if auth else None
            if not user_id:
                logger.warning(f"Socket.IO connect: sid={sid} (user_id unknown at connect).")
                return False

            logger.info(f"Socket.IO connect: sid={sid}. Connection established, awaiting join_user_room.")

        @sio.event
        async def disconnect(sid):
            """Handle a Socket.IO disconnection."""
            user_id = self._remove_sid(sid)
            logger.info(f"Socket.IO disconnect: sid={sid}, user_id={user_id or 'unknown'}")

        # --- Custom Events: Client joins/leaves rooms dynamically ---

        @sio.event
        async def join_user_room(sid, data: dict[str, Any]):
            """Client requests to join a user-specific room. Should be the first event sent after connecting."""
            user_id = data.get("user_id")
            if not user_id:
                logger.warning(f"Invalid join_user_room request from {sid}: Missing user_id.")
                await sio.emit(
                    "room_join_ack",
                    {"status": "failure", "message": "Missing user_id"},
                    room=sid,
                )
                return

            room_name = f"user_{user_id}"
            await sio.enter_room(sid, room_name)

            self._sid_to_user_id[sid] = user_id
            self._user_id_to_sids.setdefault(user_id, set()).add(sid)

            logger.info(f"Socket {sid} (user_id={user_id}) joined user room: {room_name}")
            await sio.emit("room_join_ack", {"room_name": room_name, "status": "success"}, room=sid)

        @sio.event
        async def leave_user_room(sid, data: dict[str, Any]):
            """Client requests to leave a user-specific room (usually not necessary unless switching accounts)."""
            user_id = data.get("user_id")
            if not user_id:
                logger.warning(f"Invalid leave_user_room request from {sid}: Missing user_id.")
                return

            room_name = f"user_{user_id}"
            await sio.leave_room(sid, room_name)

            self._remove_sid(sid)
            logger.info(f"Socket {sid} (user_id={user_id}) left user room: {room_name}")
            await sio.emit(
                "room_leave_ack",
                {"room_name": room_name, "status": "success"},
                room=sid,
            )

        @sio.event
        async def join_workspace_room(sid, data: dict[str, Any]):
            """Client requests to join a workspace room."""
            user_id = self._sid_to_user_id.get(sid)
            workspace_id = data.get("workspace_id")

            if not user_id or not workspace_id:
                logger.warning(f"Invalid join_workspace_room request from {sid}: user_id={user_id}, data={data}")
                await sio.emit(
                    "room_join_ack",
                    {"status": "failure", "message": "Missing user_id or workspace_id"},
                    room=sid,
                )
                return

            room_name = f"workspace_{workspace_id}"
            await sio.enter_room(sid, room_name)
            logger.info(f"Socket {sid} (user_id={user_id}) joined workspace room: {room_name}")
            await sio.emit("room_join_ack", {"room_name": room_name, "status": "success"}, room=sid)

        @sio.event
        async def leave_workspace_room(sid, data: dict[str, Any]):
            """Client requests to leave a workspace room."""
            user_id = self._sid_to_user_id.get(sid)
            workspace_id = data.get("workspace_id")
            if not user_id or not workspace_id:
                logger.warning(f"Invalid leave_workspace_room request from {sid}: {data}")
                return

            room_name = f"workspace_{workspace_id}"
            await sio.leave_room(sid, room_name)
            logger.info(f"Socket {sid} (user_id={user_id}) left workspace room: {room_name}")
            await sio.emit(
                "room_leave_ack",
                {"room_name": room_name, "status": "success"},
                room=sid,
            )

        @sio.event
        async def join_channel_room(sid, data: dict[str, Any]):
            """Client requests to join a channel room."""
            user_id = self._sid_to_user_id.get(sid)
            channel_id = data.get("channel_id")
            workspace_id = data.get("workspace_id")

            if not user_id or not channel_id or not workspace_id:
                logger.warning(f"Invalid join_channel_room request from {sid}: data={data}")
                await sio.emit(
                    "room_join_ack",
                    {"status": "failure", "message": "Missing required IDs"},
                    room=sid,
                )
                return

            room_name = f"channel_{channel_id}"
            await sio.enter_room(sid, room_name)

            # Add the user to channel_subscriptions
            if channel_id not in self._channel_subscriptions:
                self._channel_subscriptions[channel_id] = set()
            self._channel_subscriptions[channel_id].add(user_id)

            logger.info(f"Socket {sid} (user_id={user_id}) joined channel room: {room_name}")
            await sio.emit("room_join_ack", {"room_name": room_name, "status": "success"}, room=sid)

        @sio.event
        async def leave_channel_room(sid, data: dict[str, Any]):
            """Client requests to leave a channel room."""
            user_id = self._sid_to_user_id.get(sid)
            channel_id = data.get("channel_id")
            if not user_id or not channel_id:
                logger.warning(f"Invalid leave_channel_room request from {sid}: {data}")
                return

            room_name = f"channel_{channel_id}"
            await sio.leave_room(sid, room_name)

            # Remove the user from channel_subscriptions
            if channel_id in self._channel_subscriptions:
                self._channel_subscriptions[channel_id].discard(user_id)
                if not self._channel_subscriptions[channel_id]:
                    del self._channel_subscriptions[channel_id]

            logger.info(f"Socket {sid} (user_id={user_id}) left channel room: {room_name}")
            await sio.emit(
                "room_leave_ack",
                {"room_name": room_name, "status": "success"},
                room=sid,
            )

    # --- Methods to emit messages to specific rooms (unchanged) ---
    def _remove_sid(self, sid: str):
        user_id = self._sid_to_user_id.pop(sid, None)
        if user_id:
            sids = self._user_id_to_sids.get(user_id)
            if sids:
                sids.discard(sid)
                if not sids:
                    self._user_id_to_sids.pop(user_id, None)

            # Remove the user from channel_subscriptions
            for channel_id in self._channel_subscriptions:
                self._channel_subscriptions[channel_id].discard(user_id)
                if not self._channel_subscriptions[channel_id]:
                    del self._channel_subscriptions[channel_id]

    async def emit_to_room(self, room_name: str, event_type: str, data: dict[str, Any]):
        """Generic method to emit an event to a specific Socket.IO room."""
        try:
            await sio.emit(event_type, data, room=room_name)
            logger.debug(f"Emitted Socket.IO event '{event_type}' to room '{room_name}'. Data: {data}")
        except Exception as e:
            logger.error(
                f"Error emitting Socket.IO event '{event_type}' to room '{room_name}': {e}",
                exc_info=True,
            )

    def get_online_users_in_channel(self, channel_id: str):
        return self._channel_subscriptions.get(channel_id, set())

    async def broadcast(self, event_type: str, data: dict[str, Any]):
        """Broadcast an event to all active connections."""
        try:
            await sio.emit(event_type, data)
            logger.info(f"Broadcasted Socket.IO event '{event_type}'. Data: {data}")
        except Exception as e:
            logger.error(f"Error broadcasting Socket.IO event '{event_type}': {e}", exc_info=True)


# Global Socket.IO manager instance
socketio_manager = SocketIOManager()
