# Auth module interface exposing schemas, services, and utilities.
# Used to decouple implementation and support future extensions.

from abc import ABC, abstractmethod

from pydantic import EmailStr

from app.modules.auth.schemas import (
    ChangePassword,
    ForgotPassword,
    Login,
    Register,
    RegisterBase,  # noqa F401
    ResetPassword,
    VerifyEmail,
)


class IAuthService(ABC):
    @abstractmethod
    async def register(self, data: Register):
        pass

    @abstractmethod
    async def login(self, data: Login):
        pass

    @abstractmethod
    async def logout(self):
        pass

    @abstractmethod
    async def forgot_password(self, data: ForgotPassword):
        pass

    @abstractmethod
    async def reset_password(self, data: ResetPassword):
        pass

    @abstractmethod
    async def change_password(self, data: ChangePassword, refresh_token: str | None = None):
        pass

    @abstractmethod
    async def verify_email(self, data: VerifyEmail):
        pass

    @abstractmethod
    async def request_verify_email(self, email: EmailStr):
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str | None):
        pass
