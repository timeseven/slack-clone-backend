from pydantic import BaseModel, EmailStr


class RegisterBase(BaseModel):
    password: str
    full_name: str


class Register(RegisterBase):
    email: EmailStr


class VerifyEmail(BaseModel):
    token: str


class RequestVerifyEmail(BaseModel):
    email: EmailStr


class Login(BaseModel):
    email: EmailStr
    password: str


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    password: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
