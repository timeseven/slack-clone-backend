import socketio

from app.core.config import settings

SOCKET_IO_BACKEND = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_SOCKET_IO_DB}"
mgr = socketio.AsyncRedisManager(SOCKET_IO_BACKEND)
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.all_cors_origins,
    client_manager=mgr,
)
