from typing import Any

from redis.asyncio import Redis

from app.core.config import settings
from app.modules.notifications.async_tasks.interface import IAsyncNotificationService
from app.modules.notifications.async_tasks.schemas import (
    EmailResetPassword,
    EmailVerification,
    EmailWorkspaceInvitation,
)
from app.modules.notifications.async_tasks.utils import (
    generate_invitation_link,
    generate_reset_password_link,
    generate_verify_link,
    render_email_template,
)
from app.modules.notifications.realtime.interface import UserEventType


class AsyncNotificationService(IAsyncNotificationService):
    def __init__(self, redis: Redis | None = None, arq_redis=None):
        self.redis = redis
        self.arq_redis = arq_redis

    async def send_email_verification(self, data: EmailVerification):
        print("send_email_verification")
        verify_link = await generate_verify_link(redis=self.redis, email=data.email)
        html_content = render_email_template(
            template_name="verify_email.html",
            context={
                "project_name": settings.PROJECT_NAME,
                "full_name": data.full_name,
                "verify_link": verify_link,
            },
        )
        await self.arq_redis.enqueue_job(
            "send_email_task", email_to=data.email, subject="Verify your email", html_content=html_content
        )

    async def send_email_reset_password(self, data: EmailResetPassword):
        reset_password_link = await generate_reset_password_link(redis=self.redis, email=data.email)

        html_content = render_email_template(
            template_name="reset_password.html",
            context={
                "project_name": settings.PROJECT_NAME,
                "full_name": data.full_name,
                "reset_password_link": reset_password_link,
            },
        )
        await self.arq_redis.enqueue_job(
            "send_email_task", email_to=data.email, subject="Reset your password", html_content=html_content
        )

    async def send_email_workspace_invitation(self, data: EmailWorkspaceInvitation):
        invitation_link = await generate_invitation_link(
            workspace_id=data.workspace_id,
            workspace_name=data.workspace_name,
            type=data.invitation_type,
            token=data.invitation_id,
            email=data.email,
        )
        html_content = render_email_template(
            template_name="workspace_invitation.html",
            context={
                "project_name": settings.PROJECT_NAME,
                "workspace_name": data.workspace_name,
                "invitee_name": data.invitee_name,
                "inviter_name": data.inviter_name,
                "invitation_link": invitation_link,
            },
        )
        await self.arq_redis.enqueue_job(
            "send_email_task",
            email_to=data.email,
            subject=f"You have been invited to join {data.workspace_name} on {settings.PROJECT_NAME}",
            html_content=html_content,
        )

    async def notify_users_event_type(self, event_type: str, user_ids: set[str], data: dict[str, Any] = None):
        match event_type:
            case UserEventType.MESSAGE_UNREAD:
                await self.arq_redis.enqueue_job(
                    "send_unread_message", user_ids=user_ids, event_type=event_type, data=data
                )
            case _:
                pass
