# Async notification module interface exposing schemas and services
# Used to decouple implementation and support future extensions.

from abc import ABC, abstractmethod
from typing import Any

from app.modules.notifications.async_tasks.schemas import (
    EmailResetPassword,
    EmailVerification,
    EmailWorkspaceInvitation,
)


class IAsyncNotificationService(ABC):
    @abstractmethod
    async def send_email_verification(self, data: EmailVerification):
        pass

    @abstractmethod
    async def send_email_reset_password(self, data: EmailResetPassword):
        pass

    @abstractmethod
    async def send_email_workspace_invitation(self, data: EmailWorkspaceInvitation):
        pass

    @abstractmethod
    async def notify_users_event_type(self, event_type: str, user_ids: set[str], data: dict[str, Any] = None):
        pass
