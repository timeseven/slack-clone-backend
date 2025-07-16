from arq.connections import RedisSettings

from app.core.config import settings
from app.modules.notifications.async_tasks.tasks.base_tasks import send_email_task
from app.modules.notifications.async_tasks.tasks.realtime_tasks import send_unread_message

REDIS_SETTINGS = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT, database=settings.REDIS_ARQ_DB)


async def startup(ctx):
    print("Arq worker starting up")
    print(f"Using Redis DB: {ctx['redis']}")


async def shutdown(ctx):
    print("Arq worker shutting down")


class WorkerSettings:
    functions = [send_email_task, send_unread_message]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_SETTINGS
