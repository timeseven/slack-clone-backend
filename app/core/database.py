from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

from app.core.config import settings

async_engine: AsyncEngine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.MAX_CONNECTIONS,
    max_overflow=settings.MAX_CONNECTIONS - settings.MIN_CONNECTIONS,
    pool_pre_ping=settings.POOL_PRE_PING,
    pool_recycle=settings.POOL_RECYCLE,
    pool_timeout=settings.POOL_TIMEOUT,
    echo=settings.ECHO,
)
