from typing import Annotated

from fastapi import Depends

from app.core.deps import DBConnDep
from app.modules.channels.deps import ChannelServiceDep
from app.modules.messages.interface import IMessageService
from app.modules.messages.repos import MessageMentionRepo, MessageReactionRepo, MessageRepo
from app.modules.messages.services import MessageService
from app.modules.notifications.async_tasks.deps import AsyncNotificationServiceDep
from app.modules.notifications.realtime.deps import RealTimeNotificationServiceDep
from app.modules.users.deps import UserServiceDep


async def get_message_reaction_repo(db: DBConnDep):
    return MessageReactionRepo(db)


MessageReactionRepoDep = Annotated[MessageReactionRepo, Depends(get_message_reaction_repo)]


async def get_message_mention_repo(db: DBConnDep):
    return MessageMentionRepo(db)


MessageMentionRepoDep = Annotated[MessageMentionRepo, Depends(get_message_mention_repo)]


async def get_message_repo(db: DBConnDep):
    return MessageRepo(db)


MessageRepoDep = Annotated[MessageRepo, Depends(get_message_repo)]


async def get_message_service(
    db: DBConnDep,
    message_repo: MessageRepoDep,
    message_mention_repo: MessageMentionRepoDep,
    message_reaction_repo: MessageReactionRepoDep,
    user_service: UserServiceDep,
    channel_service: ChannelServiceDep,
    async_notification_service: AsyncNotificationServiceDep,
    real_time_notification_service: RealTimeNotificationServiceDep,
) -> IMessageService:
    return MessageService(
        db=db,
        message_repo=message_repo,
        message_mention_repo=message_mention_repo,
        message_reaction_repo=message_reaction_repo,
        user_service=user_service,
        channel_service=channel_service,
        async_notification_service=async_notification_service,
        real_time_notification_service=real_time_notification_service,
    )


MessageServiceDep = Annotated[IMessageService, Depends(get_message_service)]
