from typing import Annotated

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy import Row

from app.core.config import settings
from app.core.deps import get_redis_client
from app.modules.auth.exceptions import InvalidPermission
from app.modules.auth.interface import IAuthService
from app.modules.auth.scheme import oauth2_scheme
from app.modules.auth.services import AuthService
from app.modules.notifications.async_tasks.deps import AsyncNotificationServiceDep
from app.modules.users.deps import UserServiceDep


def get_auth_service(
    user_service: UserServiceDep,
    async_notification_service: AsyncNotificationServiceDep,
    redis: Annotated[Redis, Depends(get_redis_client)],
    response: ORJSONResponse,
) -> IAuthService:
    return AuthService(
        user_service=user_service, async_notification_service=async_notification_service, redis=redis, response=response
    )


AuthServiceDep = Annotated[IAuthService, Depends(get_auth_service)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserServiceDep,
) -> Row:
    user = await user_service.get_user_from_token(token=token, secret_key=settings.ACCESS_SECRET_KEY)
    return user


UserDep = Annotated[Row, Depends(get_current_user)]


async def get_current_superuser(user: UserDep):
    if not user.is_superuser:
        raise InvalidPermission
    return user


SuperUserDep = Annotated[dict, Depends(get_current_superuser)]
