from typing import Annotated

import boto3
from fastapi import Depends

from app.core.deps import DBConnDep
from app.modules.files.interface import IFileService
from app.modules.files.repos import FileRepo
from app.modules.files.s3_client import get_s3_client
from app.modules.files.services import FileService


async def get_file_repo(db: DBConnDep):
    return FileRepo(db)


FileRepoDep = Annotated[FileRepo, Depends(get_file_repo)]


async def get_file_service(
    file_repo: FileRepoDep, s3_client: Annotated[boto3.client, Depends(get_s3_client)]
) -> IFileService:
    return FileService(file_repo=file_repo, s3_client=s3_client)


FileServiceDep = Annotated[IFileService, Depends(get_file_service)]
