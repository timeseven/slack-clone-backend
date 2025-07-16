from datetime import datetime, timedelta, timezone

from slugify import slugify

from app.core.config import settings
from app.core.utils import compute_update_fields_from_dict, generate_short_id, get_password_hash
from app.modules.files.interface import FileUpdate, IFileService
from app.modules.notifications.async_tasks.interface import EmailWorkspaceInvitation, IAsyncNotificationService
from app.modules.notifications.realtime.interface import IRealtimeNotificationService, UserEventType, WorkspaceEventType
from app.modules.users.interface import IUserService, UserDBCreate, UserDBUpdate, UserRead
from app.modules.workspaces.exceptions import (
    WSBadRequest,
    WSInvitationBadRequest,
    WSNameValidationError,
    WSNotFound,
)
from app.modules.workspaces.interface import IWorkspaceService
from app.modules.workspaces.repos import WorkspaceInvitationRepo, WorkspaceMembershipRepo, WorkspaceRepo
from app.modules.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceInvitationDBCreate,
    WorkspaceInvitationDBUpdate,
    WorkspaceInvite,
    WorkspaceJoin,
    WorkspaceMemberRoleEnum,
    WorkspaceMembershipDBCreate,
    WorkspaceMembershipDBUpdate,
    WorkspaceSwitch,
    WorkspaceTransfer,
    WorkspaceUpdate,
)


class WorkspaceService(IWorkspaceService):
    def __init__(
        self,
        workspace_repo: WorkspaceRepo,
        workspace_membership_repo: WorkspaceMembershipRepo,
        workspace_invitation_repo: WorkspaceInvitationRepo,
        user_service: IUserService,
        file_service: IFileService,
        async_notification_service: IAsyncNotificationService,
        real_time_notification_service: IRealtimeNotificationService,
    ):
        self.workspace_repo = workspace_repo
        self.workspace_membership_repo = workspace_membership_repo
        self.workspace_invitation_repo = workspace_invitation_repo
        self.user_service = user_service
        self.file_service = file_service
        self.async_notification_service = async_notification_service
        self.real_time_notification_service = real_time_notification_service

    async def get_workspaces_by_user(self, user_id: str):
        memberships = await self.workspace_membership_repo.get_list_by_user(user_id)
        workspace_ids = [m.workspace_id for m in memberships]

        workspaces = await self.workspace_repo.get_list_by_ids(workspace_ids)
        workspace_map = {w.id: dict(w._mapping) for w in workspaces}

        result = []
        for m in memberships:
            workspace = workspace_map.get(m.workspace_id)
            if workspace:
                workspace["membership"] = m
                result.append(workspace)
        return result

    async def create_workspace(self, user_id: str, data: WorkspaceCreate):
        if await self.workspace_repo.get_one_by_name(data.name):
            raise WSNameValidationError("Workspace name already exists")

        if await self.workspace_membership_repo.count_owned_by_user(user_id) >= 3:
            raise WSBadRequest(detail="You reached the maximum number of workspaces")

        slug = slugify(data.name)
        workspace_id = generate_short_id("W")

        await self.workspace_repo.create(workspace_id=workspace_id, data={"name": data.name, "slug": slug})

        if data.logo:
            file = await self.file_service.update_file(file_id=data.logo, data=FileUpdate(workspace_id=workspace_id))
            await self.workspace_repo.update(workspace_id, data={"logo": file.filepath})

        existing = await self.workspace_membership_repo.get_active_one_by_user(user_id)
        if existing:
            await self.workspace_membership_repo.update(
                workspace_id=existing.workspace_id, user_id=user_id, data={"is_active": False}
            )

        await self.workspace_membership_repo.create(
            workspace_id=workspace_id,
            user_id=user_id,
            data={"role": WorkspaceMemberRoleEnum.OWNER, "is_active": True},
        )

        return workspace_id

    async def get_workspace(self, workspace_id: str, user_id: str):
        workspace = await self.workspace_repo.get_one_by_id(workspace_id)
        if workspace is None:
            raise WSNotFound

        membership = await self.workspace_membership_repo.get_one_by_workspace_and_user(workspace_id, user_id)
        w = dict(workspace._mapping)
        w["membership"] = membership

        all_memberships = await self.workspace_membership_repo.get_one_by_workspace(workspace_id)
        user_ids = list({m.user_id for m in all_memberships})
        users = await self.user_service.get_users_by_ids(user_ids)
        user_map = {u.id: dict(u._mapping) for u in users}

        role_priority = {"owner": 0, "admin": 1, "member": 2}
        workspace_members_map = []
        for m in all_memberships:
            user = user_map.get(m.user_id)
            if user:
                member = {
                    **user,
                    "role": m.role,
                }
                workspace_members_map.append(member)

        workspace_members_map.sort(key=lambda m: role_priority.get(m["role"], 99))
        w["members"] = workspace_members_map
        return w

    async def get_workspace_membership(self, workspace_id: str, user_id: str):
        return await self.workspace_membership_repo.get_one_by_workspace_and_user(workspace_id, user_id)

    async def update_workspace(self, workspace_id: str, data: WorkspaceUpdate):
        old = await self.workspace_repo.get_one_by_id(workspace_id)
        update_data = compute_update_fields_from_dict(old=old, new_data=data.model_dump(), include_none_fields=["logo"])
        if not update_data:
            return old

        if "name" in update_data:
            if await self.workspace_repo.get_one_by_name(update_data["name"]):
                raise WSNameValidationError("Workspace name already exists")
            update_data["slug"] = slugify(update_data["name"])

        if update_data.get("logo") and "amazonaws" not in update_data["logo"]:
            file = await self.file_service.update_file(
                file_id=update_data["logo"], data=FileUpdate(workspace_id=workspace_id)
            )
            update_data["logo"] = file.filepath

        workspace = await self.workspace_repo.update(workspace_id, data=update_data)
        if workspace is None:
            raise WSNotFound

        await self.real_time_notification_service.send_to_workspace(
            workspace_id, WorkspaceEventType.WORKSPACE_UPDATE, {"id": workspace_id, **update_data}
        )
        return workspace

    async def delete_workspace(self, workspace_id: str):
        await self.workspace_repo.delete(workspace_id)
        await self.real_time_notification_service.send_to_workspace(
            workspace_id, WorkspaceEventType.WORKSPACE_DELETE, {"workspace_id": workspace_id}
        )

    async def transfer_ownership(self, workspace_id: str, user_id: str, data: WorkspaceTransfer):
        if user_id == data.user_id:
            raise WSBadRequest("You are already the owner")

        await self.workspace_membership_repo.update(workspace_id, user_id, {"role": WorkspaceMemberRoleEnum.MEMBER})

        if await self.workspace_membership_repo.get_one_by_workspace_and_user(workspace_id, data.user_id):
            await self.workspace_membership_repo.update(
                workspace_id, data.user_id, {"role": WorkspaceMemberRoleEnum.OWNER}
            )
        else:
            is_active = not await self.workspace_membership_repo.get_active_one_by_user(data.user_id)
            await self.workspace_membership_repo.create(
                workspace_id=workspace_id,
                user_id=data.user_id,
                data=WorkspaceMembershipDBCreate(role="owner", is_active=is_active).model_dump(),
            )

        await self.real_time_notification_service.send_to_workspace(
            workspace_id, WorkspaceEventType.WORKSPACE_TRANSFER, {"workspace_id": workspace_id}
        )

    async def switch_workspace(self, user_id: str, data: WorkspaceSwitch, workspace_id: str | None = None):
        if workspace_id:
            await self.workspace_membership_repo.update(workspace_id, user_id, {"is_active": False})
        await self.workspace_membership_repo.update(data.workspace_id, user_id, {"is_active": True})

    async def invite_to_workspace(self, workspace_id: str, user_id: str, data: WorkspaceInvite):
        workspace = await self.workspace_repo.get_one_by_id(workspace_id)
        if not workspace:
            raise WSNotFound

        inviter = await self.user_service.get_user_by_id(user_id)
        email_set = set(data.emails)
        users = await self.user_service.get_users_by_emails(list(email_set))
        user_map = {u.email: u for u in users}

        memberships = await self.workspace_membership_repo.get_one_by_workspace(workspace_id)
        member_ids = {m.user_id for m in memberships}

        invitee_ids = [u.id for u in users]
        invitations = await self.workspace_invitation_repo.get_list_by_workspace_and_invitees(workspace_id, invitee_ids)
        invitation_map = {inv.invitee_id: inv for inv in invitations}

        for email in data.emails:
            invitee = user_map.get(email)
            invitee_id = None
            invitee_name = email
            invitation_type = "join"

            if invitee:
                invitee_id = invitee.id
                invitee_name = invitee.full_name or email

                if invitee.hashed_password and invitee.id in member_ids:
                    continue
                if not invitee.hashed_password:
                    invitation_type = "rookie"
            else:
                invitee_id = await self.user_service.create_user(
                    UserDBCreate(email=email, full_name=email, hashed_password=None)
                )
                invitation_type = "rookie"

            if invitee_id in invitation_map:
                await self.workspace_invitation_repo.delete(invitation_map[invitee_id].id)

            invitation_id = generate_short_id("WI")
            await self.workspace_invitation_repo.create(
                invitation_id=invitation_id,
                data=WorkspaceInvitationDBCreate(
                    workspace_id=workspace_id,
                    inviter_id=user_id,
                    invitee_id=invitee_id,
                ).model_dump(),
            )

            if settings.SMTP_ENABLED:
                await self.async_notification_service.send_email_workspace_invitation(
                    EmailWorkspaceInvitation(
                        workspace_id=workspace_id,
                        workspace_name=workspace.name,
                        email=email,
                        invitation_type=invitation_type,
                        invitation_id=invitation_id,
                        invitee_name=invitee_name,
                        inviter_name=inviter.full_name,
                    )
                )

    async def join_workspace(self, workspace_id: str, data: WorkspaceJoin):
        user = await self.user_service.get_user_by_email(data.email)
        invitation = await self.workspace_invitation_repo.get_one_by_id(data.token)

        if (
            not invitation
            or datetime.now(timezone.utc) - invitation.created_at > timedelta(hours=72)
            or invitation.workspace_id != workspace_id
            or invitation.invitee_id != user.id
        ):
            raise WSInvitationBadRequest("Invitation invalid or expired")

        if invitation.status != "pending":
            raise WSInvitationBadRequest("Invitation already used")

        if data.user_data:
            await self.user_service.update_user(
                user.id,
                UserDBUpdate(
                    full_name=data.user_data.full_name,
                    hashed_password=get_password_hash(data.user_data.password),
                    is_verified=True,
                ),
            )

        is_active = not await self.workspace_membership_repo.get_active_one_by_user(user.id)
        await self.workspace_membership_repo.create(
            workspace_id,
            user.id,
            WorkspaceMembershipDBCreate(role="member", is_active=is_active).model_dump(),
        )

        await self.workspace_invitation_repo.update(
            invitation.id, WorkspaceInvitationDBUpdate(status="accepted").model_dump()
        )

        await self.real_time_notification_service.send_to_workspace(
            workspace_id, WorkspaceEventType.WORKSPACE_JOIN, {"workspace_id": workspace_id}
        )

    async def leave_workspace(self, workspace_id: str, user_id: str):
        await self.workspace_membership_repo.delete(workspace_id, user_id)
        await self.real_time_notification_service.send_to_workspace(
            workspace_id, WorkspaceEventType.WORKSPACE_LEAVE, {"workspace_id": workspace_id}
        )

    async def remove_from_workspace(self, workspace_id: str, user_id: str):
        await self.workspace_membership_repo.delete(workspace_id, user_id)
        await self.real_time_notification_service.send_to_user(
            user_id, UserEventType.WORKSPACE_REMOVE, {"workspace_id": workspace_id}
        )
        await self.real_time_notification_service.send_to_workspace(
            workspace_id, WorkspaceEventType.WORKSPACE_LEAVE, {"workspace_id": workspace_id}
        )

    async def set_workspace_role(self, workspace_id, data):
        await self.workspace_membership_repo.update(workspace_id, data.user_id, {"role": data.role})
        # notify workspace members
        await self.real_time_notification_service.send_to_workspace(
            workspace_id, WorkspaceEventType.WORKSPACE_ROLE_UPDATE, {"workspace_id": workspace_id}
        )
