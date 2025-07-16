from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Table, Text, func, text
from sqlalchemy.dialects.postgresql import ENUM

from app.core.models import metadata

ChannelType = ENUM("channel", "dm", "group_dm", name="channel_type", create_type=True)
Channel = Table(
    "channels",
    metadata,
    Column("id", String(36), primary_key=True, nullable=False),
    Column("workspace_id", ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("name", String(255), nullable=True),
    Column("description", String(255), nullable=True),
    Column("type", ChannelType, nullable=False, server_default=text("'channel'")),
    Column("is_private", Boolean, nullable=False, server_default=text("false")),
    Column(
        "last_message",
        Text,
        nullable=True,
    ),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    ),
)

ChannelMemberRole = ENUM("owner", "admin", "member", name="channel_member_role", create_type=True)

ChannelMembership = Table(
    "channel_memberships",
    metadata,
    Column(
        "channel_id",
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True),
    Column("workspace_id", ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("role", ChannelMemberRole, nullable=False, server_default=text("'member'")),
    Column("is_starred", Boolean, nullable=False, server_default=text("false")),
    Column("is_muted", Boolean, nullable=False, server_default=text("false")),
    Column("last_read_at", DateTime(timezone=True), nullable=True),
    Column("unread_count", Integer, nullable=False, server_default=text("0")),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    ),
    Index(None, "channel_id", unique=True, postgresql_where=text("role = 'owner'")),
)
