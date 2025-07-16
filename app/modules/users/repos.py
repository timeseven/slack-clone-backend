from pydantic import EmailStr
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.modules.users.models import User


class UserRepo:
    def __init__(self, db: AsyncConnection):
        self.db = db

    async def get_one_by_email(self, email: EmailStr):
        stmt = select(User).where(User.c.email == email).limit(1)
        return (await self.db.execute(stmt)).first()

    async def get_list_by_emails(self, emails: list[EmailStr]):
        stmt = select(User).where(User.c.email.in_(emails))
        return (await self.db.execute(stmt)).fetchall()

    async def get_one_by_id(self, user_id: str):
        stmt = select(User).where(User.c.id == user_id).limit(1)
        return (await self.db.execute(stmt)).first()

    async def get_list_by_ids(self, user_ids: list[str]):
        stmt = select(User).where(User.c.id.in_(user_ids))
        return (await self.db.execute(stmt)).fetchall()

    async def create(self, user_id: str, data: dict) -> str:
        stmt = insert(User).values(id=user_id, **data)
        await self.db.execute(stmt)

    async def update(self, user_id: str, data: dict):
        stmt = update(User).where(User.c.id == user_id).values(**data).returning(User)
        result = await self.db.execute(stmt)
        return result.first()

    # Hard delete
    async def delete(self, user_id: str):
        stmt = delete(User).where(User.c.id == user_id)
        await self.db.execute(stmt)
