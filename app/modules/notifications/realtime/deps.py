from typing import Annotated

from fastapi import Depends

from app.modules.notifications.realtime.interface import IRealtimeNotificationService
from app.modules.notifications.realtime.services import RealtimeNotificationService
from app.modules.notifications.realtime.socketio_manager import socketio_manager


async def get_real_time_notification_service() -> IRealtimeNotificationService:
    return RealtimeNotificationService(socketio_manager=socketio_manager)


RealTimeNotificationServiceDep = Annotated[
    IRealtimeNotificationService,
    Depends(get_real_time_notification_service),
]
