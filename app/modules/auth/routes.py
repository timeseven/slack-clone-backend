from typing import Annotated

from fastapi import APIRouter, Cookie, status

from app.core.response import success_response
from app.core.schemas import CustomResponse
from app.modules.auth.deps import AuthServiceDep, UserDep
from app.modules.auth.schemas import (
    ChangePassword,
    ForgotPassword,
    Login,
    Register,
    RequestVerifyEmail,
    ResetPassword,
    VerifyEmail,
)

auth_router = APIRouter(tags=["auth"])


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=CustomResponse,
)
async def register(
    auth_service: AuthServiceDep,
    data: Register,
):
    await auth_service.register(data)
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="User registered successfully",
    )


@auth_router.post("/login", response_model=CustomResponse)
async def login(
    auth_service: AuthServiceDep,
    data: Login,
):
    response = await auth_service.login(data=data)
    return success_response(response=response, message="Login successfully")


@auth_router.post("/logout", response_model=CustomResponse)
async def logout(
    auth_service: AuthServiceDep,
):
    response = await auth_service.logout()
    return success_response(response=response, message="Logout successfully")


@auth_router.post("/forgot-password", response_model=CustomResponse)
async def forgot_password(
    auth_service: AuthServiceDep,
    data: ForgotPassword,
):
    await auth_service.forgot_password(email=data.email)
    return success_response(message="An email has been sent to you")


@auth_router.post("/reset-password", response_model=CustomResponse)
async def reset_password(
    auth_service: AuthServiceDep,
    data: ResetPassword,
):
    await auth_service.reset_password(token=data.token, password=data.password)
    return success_response(message="Password reset successfully")


@auth_router.post("/change-password")
async def change_password(
    auth_service: AuthServiceDep,
    user: UserDep,
    data: ChangePassword,
    refresh_token: Annotated[
        str | None,
        Cookie(alias="refresh_token"),
    ] = None,
):
    await auth_service.change_password(user=user, data=data)
    response = await auth_service.logout(refresh_token=refresh_token)
    return success_response(response=response, message="Password changed successfully")


@auth_router.post("/verify", response_model=CustomResponse)
async def verify_email(auth_service: AuthServiceDep, data: VerifyEmail):
    await auth_service.verify_email(token=data.token)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Email verified successfully",
    )


@auth_router.post("/request-verify", response_model=CustomResponse)
async def request_verify_email(auth_service: AuthServiceDep, data: RequestVerifyEmail):
    await auth_service.request_verify_email(email=data.email)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="An email has been sent to you",
    )


@auth_router.post("/refresh-token", response_model=CustomResponse)
async def refresh_token(
    auth_service: AuthServiceDep,
    refresh_token: Annotated[str, Cookie(alias="refresh_token")],
):
    response = await auth_service.refresh_token(refresh_token=refresh_token)
    return success_response(response=response, message="Token refreshed successfully")
