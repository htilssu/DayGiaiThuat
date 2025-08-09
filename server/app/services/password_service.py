from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_async_db
from app.models.user_model import User
from app.utils.utils import password_hash


def get_password_service(db: AsyncSession = Depends(get_async_db)):
    return PasswordService(db)


class PasswordService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def change_password(self, user_id: int, new_password: str) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.hashed_password = password_hash(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user
