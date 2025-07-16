from typing import Annotated

from fastapi import Depends

from app.core.deps import DBConnDep
from app.modules.files.deps import FileServiceDep
from app.modules.users.repos import UserRepo
from app.modules.users.services import IUserService, UserService


async def get_user_repo(db: DBConnDep):
    return UserRepo(db)


UserRepoDep = Annotated[DBConnDep, Depends(get_user_repo)]


async def get_user_service(user_repo: UserRepoDep, file_service: FileServiceDep) -> IUserService:
    return UserService(user_repo=user_repo, file_service=file_service)


UserServiceDep = Annotated[IUserService, Depends(get_user_service)]
