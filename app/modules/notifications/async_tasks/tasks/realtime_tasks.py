from typing import Any

from app.modules.notifications.realtime.deps import get_real_time_notification_service


async def send_unread_message(ctx, *, user_ids: set[str], event_type: str, data: dict[str, Any]):
    real_time_notification_service = await get_real_time_notification_service()
    for user_id in user_ids:
        await real_time_notification_service.send_to_user(
            user_id,
            event_type=event_type,
            data=data,
        )
