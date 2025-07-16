from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, func, text
from sqlalchemy.dialects.postgresql import ENUM, JSONB

from app.core.models import metadata

MessageType = ENUM("message_user", "message_system", "changelog", "notes", name="message_type", create_type=True)

Message = Table(
    "messages",
    metadata,
    Column("id", String(36), primary_key=True, nullable=False),
    Column("workspace_id", ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("channel_id", ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("parent_id", ForeignKey("messages.id", ondelete="CASCADE"), nullable=True),
    Column("content", JSONB, nullable=True),
    Column("message_type", MessageType, nullable=False, server_default=text("'message_user'")),
    Column("is_pinned", Boolean, nullable=False, server_default=text("false")),
    Column("sender_id", ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    ),
)

Reactions = Table(
    "message_reactions",
    metadata,
    Column("id", String(36), primary_key=True, nullable=False),
    Column("workspace_id", ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("message_id", ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("emoji", String(255), nullable=False),
    Column("sender_id", ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

Mentions = Table(
    "message_mentions",
    metadata,
    Column("id", String(36), primary_key=True, nullable=False),
    Column("workspace_id", ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("message_id", ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE")),
    Column("start_index", Integer, nullable=True),
    Column("end_index", Integer, nullable=True),
    Column("mention_text", String, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
