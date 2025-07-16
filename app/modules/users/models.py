from sqlalchemy import Boolean, Column, DateTime, Index, String, Table, func, text

from app.core.models import metadata

User = Table(
    "users",
    metadata,
    Column("id", String(36), primary_key=True, nullable=False),
    Column("email", String(255), nullable=False, unique=True),
    Column("hashed_password", String(255), nullable=True),
    Column("full_name", String(255), nullable=False),
    Column("avatar", String(512), nullable=True),
    Column("status", String(255), nullable=True),
    Column("is_active", Boolean, nullable=False, server_default=text("false")),
    Column("is_verified", Boolean, nullable=False, server_default=text("false")),
    Column("is_superuser", Boolean, nullable=False, server_default=text("false")),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("last_login_at", DateTime(timezone=True), nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    ),
    Index(None, "email", "full_name"),
)
