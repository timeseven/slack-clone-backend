from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile

from app.core.response import success_response
from app.core.schemas import CustomResponse
from app.modules.auth.deps import SuperUserDep, UserDep
from app.modules.users.deps import UserServiceDep
from app.modules.users.exceptions import UserNotFound
from app.modules.users.schemas import UserProfileUpdate, UserRead

user_router = APIRouter(tags=["users"])


@user_router.get("/me", response_model=CustomResponse[UserRead])
async def read_me(user: UserDep):
    return success_response(
        data=UserRead.model_validate(user, from_attributes=True),
        message="User retrieved successfully",
    )


@user_router.patch("/me", response_model=CustomResponse[UserRead])
async def update_me_profile(
    user: UserDep,
    user_service: UserServiceDep,
    data: UserProfileUpdate,
):
    user = await user_service.update_user(user_id=user.id, data=data)
    return success_response(
        data=UserRead.model_validate(user, from_attributes=True),
        message="User updated successfully",
    )


@user_router.post("/me/upload-avatar", response_model=CustomResponse[UserRead])
async def update_me_avatar(
    user: UserDep,
    user_service: UserServiceDep,
    file: UploadFile,
):
    user = await user_service.upload_avatar(user_id=user.id, file=file)
    return success_response(
        data=UserRead.model_validate(user, from_attributes=True),
        message="User updated successfully",
    )


@user_router.get("/{user_id}", response_model=CustomResponse[UserRead])
async def read_user(
    user_id: str,
    user_service: UserServiceDep,
):
    user = await user_service.get_user_by_id(user_id=user_id)
    if user is None:
        raise UserNotFound
    return success_response(
        data=UserRead.model_validate(user, from_attributes=True),
        message="User retrieved successfully",
    )


@user_router.patch("/{user_id}", response_model=CustomResponse[UserRead])
async def update_user(
    super_user: SuperUserDep,
    user_id: str,
    user_service: UserServiceDep,
    data: UserProfileUpdate,
):
    user = await user_service.update_user(user_id=user_id, data=data)
    return success_response(
        data=UserRead.model_validate(user, from_attributes=True),
        message="User updated successfully",
    )


@user_router.delete("/{user_id}", response_model=CustomResponse)
async def delete_user(
    super_user: SuperUserDep,
    user_id: str,
    user_service: UserServiceDep,
):
    await user_service.delete_user(user_id=user_id)
    return success_response(message="User deleted successfully")
