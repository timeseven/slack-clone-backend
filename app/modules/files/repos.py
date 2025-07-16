from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.files.models import File


class FileRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_one_by_id(self, file_id: str):
        stmt = select(File).where(File.c.id == file_id)
        result = await self.db.execute(stmt)
        return result.first()

    async def create(self, file_id: str, data: dict):
        stmt = insert(File).values(id=file_id, **data)
        await self.db.execute(stmt)

    async def update(self, file_id: str, data: dict):
        stmt = update(File).where(File.c.id == file_id).values(**data).returning(File)
        result = await self.db.execute(stmt)
        return result.first()

    async def delete(self, file_id: str):
        stmt = File.delete().where(File.c.id == file_id)
        await self.db.execute(stmt)
