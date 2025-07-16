from loguru import logger
from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings


class RedisClient:
    def __init__(
        self,
        host: str,
        port: int,
        db: int = 0,
        decode_responses: bool = True,
    ):
        self._client = None

        self._pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses,
        )

    def get_client(self):
        if self._client is None:
            self._client = Redis(connection_pool=self._pool)
        return self._client

    async def connect(self):
        try:
            client = self.get_client()
            await client.ping()
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            logger.error(f"Redis async connection failed: {e}")  # <--- Use loguru logger
            raise RuntimeError("Redis async connection failed") from e

    async def disconnect(self):
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Disconnected from Redis.")


redis_client = RedisClient(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DEFAULT_DB,
    decode_responses=True,
)
