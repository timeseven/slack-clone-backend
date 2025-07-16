from typing import Annotated

from fastapi import Depends

from app.core.deps import ArqRedisDep, RedisDep
from app.modules.notifications.async_tasks.interface import IAsyncNotificationService
from app.modules.notifications.async_tasks.services import AsyncNotificationService


async def get_async_notification_service(redis: RedisDep, arq_redis: ArqRedisDep) -> IAsyncNotificationService:
    return AsyncNotificationService(redis=redis, arq_redis=arq_redis)


AsyncNotificationServiceDep = Annotated[IAsyncNotificationService, Depends(get_async_notification_service)]
