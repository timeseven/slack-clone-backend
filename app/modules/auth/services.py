import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.responses import ORJSONResponse
from pydantic import EmailStr
from redis.asyncio import Redis
from sqlalchemy import Row

from app.core.config import settings
from app.core.utils import delete_redis_value, get_password_hash, get_redis_value, set_redis_value, verify_password
from app.modules.auth.exceptions import (
    AuthEmailValidationError,
    AuthPasswordValidationError,
    InvalidCredentials,
    InvalidToken,
)
from app.modules.auth.interface import IAuthService
from app.modules.auth.schemas import ChangePassword, Login, Register
from app.modules.auth.utils import generate_token, set_token_cookies
from app.modules.notifications.async_tasks.interface import (
    EmailResetPassword,
    EmailVerification,
    IAsyncNotificationService,
)
from app.modules.users.interface import IUserService, UserDBCreate, UserDBUpdate

MAX_DEVICES = 3


class AuthService(IAuthService):
    def __init__(
        self,
        user_service: IUserService,
        async_notification_service: IAsyncNotificationService,
        redis: Redis | None = None,
        response: ORJSONResponse | None = None,
    ):
        self.redis = redis
        self.response = response
        self.user_service = user_service
        self.async_notification_service = async_notification_service

    async def register(self, data: Register):
        hashed_password = get_password_hash(data.password)

        user_id = await self.user_service.create_user(
            data=UserDBCreate(
                email=data.email,
                hashed_password=hashed_password,
                full_name=data.full_name,
            )
        )

        if user_id and settings.SMTP_ENABLED:
            # Send verification email
            await self.async_notification_service.send_email_verification(
                data=EmailVerification(
                    email=data.email,
                    full_name=data.full_name,
                )
            )

    async def verify_email(self, token: str):
        email = await get_redis_value(redis=self.redis, name=f"verify_token_{token}")
        if email is None:
            raise InvalidToken(detail="Invalid verify token")

        user = await self.user_service.get_user_by_email(email=email)
        if user is None:
            raise InvalidToken(detail="Invalid verify token")

        await self.user_service.update_user(user_id=user.id, data=UserDBUpdate(is_verified=True))
        await delete_redis_value(redis=self.redis, name=f"verify_token_{token}")

    async def login(self, data: Login):
        user = await self.user_service.authenticate_user(email=data.email, password=data.password)

        # Generate access token
        access_token, access_expires_at = generate_token(
            "access_token",
            settings.ACCESS_SECRET_KEY,
            settings.ALGORITHM,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            str(user.id),
        )

        # Create refresh token for multiple devices
        refresh_token_id = str(uuid4())
        refresh_token, refresh_expires_at = generate_token(
            "refresh_token",
            settings.REFRESH_SECRET_KEY,
            settings.ALGORITHM,
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            str(user.id),
        )

        # Store refresh token by refresh_token_id
        await set_redis_value(
            redis=self.redis,
            name=f"refresh_token:{refresh_token_id}",
            value=json.dumps(
                {
                    "user_id": str(user.id),
                    "refresh_token": refresh_token,
                    "created_at": datetime.now(tz=timezone.utc).isoformat(),
                }
            ),
            expires_in=refresh_expires_at,
        )

        # Track all token_ids for this user
        await self.redis.lpush(f"user_refresh_tokens:{user.id}", refresh_token_id)

        # Enforce device limit: kick out oldest if necessary
        token_ids = await self.redis.lrange(f"user_refresh_tokens:{user.id}", 0, -1)
        if len(token_ids) > MAX_DEVICES:
            excess_ids = token_ids[MAX_DEVICES:]
            for token_id in excess_ids:
                await self.redis.delete(f"refresh_token:{token_id}")
                await self.redis.lrem(f"user_refresh_tokens:{user.id}", 0, token_id)
        # Ensure only MAX_DEVICES are stored
        await self.redis.ltrim(f"user_refresh_tokens:{user.id}", 0, MAX_DEVICES - 1)

        # Set cookies
        set_token_cookies(
            self.response,
            access_token,
            access_expires_at,
            refresh_token_id,  # Return refresh_token_id instead of refresh_token
            refresh_expires_at,
        )

        # Update last login
        await self.user_service.update_user(
            user_id=user.id,
            data=UserDBUpdate(last_login_at=datetime.now(tz=timezone.utc), is_active=True),
        )

        return self.response

    async def logout(self):
        self.response.delete_cookie("access_token")
        self.response.delete_cookie("refresh_token")

        return self.response

    async def forgot_password(self, email: str):
        user = await self.user_service.get_user_by_email(email=email)
        if user is None:
            raise AuthEmailValidationError("User not found with this email")

        if settings.SMTP_ENABLED:
            # Send reset password email
            await self.async_notification_service.send_email_reset_password(
                data=EmailResetPassword(
                    email=email,
                    full_name=user.full_name,
                )
            )

    async def reset_password(self, token: str, password: str):
        email = await get_redis_value(redis=self.redis, name=f"reset_password_token_{token}")
        if email is None:
            raise InvalidToken(detail="Invalid reset password token")

        user = await self.user_service.get_user_by_email(email=email)
        if user is None:
            raise InvalidToken(detail="Invalid reset password token")

        await self.user_service.update_user(
            user_id=user.id,
            data=UserDBUpdate(hashed_password=get_password_hash(password)),
        )
        await delete_redis_value(redis=self.redis, name=f"reset_password_token_{token}")

    async def change_password(self, user: Row, data: ChangePassword):
        if not verify_password(data.old_password, user.hashed_password):
            raise AuthPasswordValidationError("Wrong old password")

        await self.user_service.update_user(
            user_id=user.id,
            data=UserDBUpdate(hashed_password=get_password_hash(data.new_password)),
        )

    async def request_verify_email(self, email: EmailStr):
        user = await self.user_service.get_user_by_email(email=email)
        if user is None:
            raise AuthEmailValidationError("User not found with this email")
        if user.is_verified:
            raise AuthEmailValidationError("User already verified")

        if settings.SMTP_ENABLED:
            await self.async_notification_service.send_email_verification(
                data=EmailVerification(
                    email=user.email,
                    full_name=user.full_name,
                )
            )

    async def refresh_token(self, refresh_token: str | None):
        if refresh_token is None:
            raise InvalidCredentials(detail="Invalid refresh token")

        redis_token_key = f"refresh_token:{refresh_token}"  # refresh_token here is refresn_token_id
        stored = await get_redis_value(redis=self.redis, name=redis_token_key)
        if not stored:
            raise InvalidCredentials(detail="Invalid refresh token")

        data = json.loads(stored)
        stored_refresh_token = data.get("refresh_token")
        user_id = data.get("user_id")

        user = await self.user_service.get_user_from_token(
            token=stored_refresh_token, secret_key=settings.REFRESH_SECRET_KEY
        )

        if user is None or str(user.id) != user_id:
            raise InvalidCredentials(detail="Invalid refresh token")

        access_token, access_expires_at = generate_token(
            "access_token",
            settings.ACCESS_SECRET_KEY,
            settings.ALGORITHM,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            str(user.id),
        )

        # Step 4: Set the new access token as an HTTP-only cookie
        set_token_cookies(self.response, access_token, access_expires_at)

        # Step 5: Update the user's last login timestamp and activate the user
        await self.user_service.update_user(
            user_id=user.id,
            data=UserDBUpdate(last_login_at=datetime.now(tz=timezone.utc)),
        )

        return self.response
