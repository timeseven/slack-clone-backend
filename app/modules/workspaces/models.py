from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM

from app.core.models import metadata

Workspace = Table(
    "workspaces",
    metadata,
    Column(
        "id",
        String(36),
        primary_key=True,
        nullable=False,
    ),
    Column("name", String(255), nullable=False, unique=True),
    Column("slug", String(255), nullable=False),
    Column("logo", String(512), nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
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
)

WorkspaceMemberRole = ENUM("owner", "admin", "member", name="workspace_member_role", create_type=True)

WorkspaceMembership = Table(
    "workspace_memberships",
    metadata,
    Column(
        "workspace_id",
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    Column("role", WorkspaceMemberRole, nullable=False, server_default=text("'member'")),
    Column("is_active", Boolean, nullable=False, server_default=text("false")),
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
    Index(None, "user_id", unique=True, postgresql_where=text("is_active = true")),
    Index(None, "workspace_id", unique=True, postgresql_where=text("role = 'owner'")),
)

InvitationStatus = ENUM("pending", "accepted", "declined", name="invitation_status", create_type=True)

WorkspaceInvitation = Table(
    "workspace_invitations",
    metadata,
    Column("id", String(36), primary_key=True, nullable=False),
    Column(
        "workspace_id",
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "invitee_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "inviter_id",
        ForeignKey(
            "users.id",
        ),
        nullable=False,
    ),
    Column("status", InvitationStatus, nullable=False, server_default=text("'pending'")),
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
    Index(None, "workspace_id", "invitee_id"),
    UniqueConstraint("workspace_id", "invitee_id"),
)
