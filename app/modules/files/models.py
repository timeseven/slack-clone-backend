from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Table, func

from app.core.models import metadata

File = Table(
    "files",
    metadata,
    Column("id", String(36), primary_key=True, nullable=False),
    Column("workspace_id", ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True),
    Column("channel_id", ForeignKey("channels.id", ondelete="SET NULL"), nullable=True, index=True),
    Column("message_id", ForeignKey("messages.id", ondelete="SET NULL"), nullable=True, index=True),
    Column("filename", String(255), nullable=False),
    Column("filepath", String(512), nullable=False),
    Column("filetype", String(255), nullable=False),
    Column("size", Integer, nullable=False),
    Column("uploader_id", ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    ),
    Index(None, "workspace_id", "channel_id"),
)
