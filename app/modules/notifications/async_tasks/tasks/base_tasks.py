from email.message import EmailMessage

import aiosmtplib
from loguru import logger

from app.core.config import settings


async def send_email_task(
    ctx,
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    message = EmailMessage()
    message["From"] = f"{settings.PROJECT_NAME} <{settings.SMTP_USER}>"
    message["To"] = email_to
    message["Subject"] = subject
    message.set_content(html_content, subtype="html")

    smtp_kwargs = {
        "hostname": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "start_tls": settings.SMTP_TLS,
        "username": settings.SMTP_USER,
        "password": settings.SMTP_PASSWORD,
    }
    try:
        await aiosmtplib.send(message, **smtp_kwargs)
        logger.info(f"Send email async success to {email_to}, subject: {subject}")
    except Exception as e:
        logger.error(f"Send email async failed to {email_to}: {e}")
