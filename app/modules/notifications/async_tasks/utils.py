import uuid
from pathlib import Path
from typing import Any

from jinja2 import Template
from redis.asyncio import Redis

from app.core.config import settings
from app.core.utils import set_redis_value


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (Path(__file__).parent / "email_templates" / "build" / template_name).read_text()
    html_content = Template(template_str).render(context)
    return html_content


async def generate_verify_link(redis: Redis, email: str) -> str:
    token = str(uuid.uuid4())
    await set_redis_value(redis, f"verify_token_{token}", email, 24 * 3600)  # Set 24 hours expiration
    verify_url = f"{settings.FRONTEND_HOST}/verify?token={token}"
    return verify_url


async def generate_reset_password_link(redis: Redis, email: str) -> str:
    token = str(uuid.uuid4())
    await set_redis_value(redis, f"reset_password_token_{token}", email, 24 * 3600)  # Set 24 hours expiration
    reset_password_url = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    return reset_password_url


# Use invitation id as token
async def generate_invitation_link(workspace_id: str, workspace_name: str, type: str, token: str, email: str) -> str:
    invite_url = (
        f"{settings.FRONTEND_HOST}/workspace/{workspace_id}/{type}"
        f"?workspace_name={workspace_name}"
        f"&token={token}"
        f"&email={email}"
    )
    return invite_url
