from pydantic import BaseModel, EmailStr


class EmailVerification(BaseModel):
    email: EmailStr
    full_name: str


class EmailResetPassword(BaseModel):
    email: EmailStr
    full_name: str


class EmailWorkspaceInvitation(BaseModel):
    workspace_id: str
    workspace_name: str
    email: EmailStr
    invitation_type: str
    invitation_id: str
    invitee_name: str
    inviter_name: str
