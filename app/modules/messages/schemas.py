from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.core.schemas import CustomModel
from app.modules.users.interface import UserRead


class MessageTypeEnum(str, Enum):
    MESSAGE_USER = "message_user"
    MESSAGE_SYSTEM = "message_system"
    MESSAGE_CHANGELOG = "changelog"
    MESSAGE_NOTES = "notes"


class ReactionCreate(BaseModel):
    emoji: str


class MentionCreate(BaseModel):
    start_index: int
    end_index: int
    mention_text: str


class MessageCreate(BaseModel):
    content: str
    parent_id: str | None = None
    message_type: MessageTypeEnum = MessageTypeEnum.MESSAGE_USER


class MessageUpdate(BaseModel):
    content: str


class ReactionRead(CustomModel):
    id: str
    emoji: str
    sender_id: str


class MetionRead(CustomModel):
    id: str
    start_index: int
    end_index: int
    mention_text: str


class MessageReadBase(CustomModel):
    id: str
    content: str
    is_pinned: bool
    workspace_id: str
    channel_id: str
    sender: UserRead | None
    created_at: datetime
    updated_at: datetime
    reactions: list[ReactionRead] | None
    mentions: list[MetionRead] | None
    message_type: MessageTypeEnum
    # files: list[str] | None


class MessageRead(MessageReadBase):
    parent_id: str | None
    replies: list[MessageReadBase] | None


class MessageCreateRead(BaseModel):
    message_id: str


class ReactionCreateRead(BaseModel):
    reaction_id: str
