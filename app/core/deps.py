from typing import Annotated, AsyncGenerator

from arq.connections import ArqRedis
from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.database import async_engine
from app.core.redis import redis_client


async def get_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with async_engine.connect() as conn:
        async with conn.begin():
            yield conn


async def get_redis_client() -> Redis:
    return redis_client.get_client()


async def get_arq_redis(request: Request) -> ArqRedis:
    return request.app.state.arq_redis


DBConnDep = Annotated[AsyncConnection, Depends(get_connection)]
RedisDep = Annotated[Redis, Depends(get_redis_client)]
ArqRedisDep = Annotated[ArqRedis, Depends(get_arq_redis)]
