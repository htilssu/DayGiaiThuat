from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, Depends

from app.core.config import settings
from app.database.database import Base, get_async_db

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession = Depends(get_async_db)):
        self.model = model
        self.db = db
        self.setting = settings

    async def get(self, id: Any) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def remove(self, *, id: int) -> ModelType:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        await self.db.delete(obj)
        await self.db.commit()
        return obj

    async def save(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_async(self, id: Any) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi_async(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def remove_async(self, *, id: int) -> ModelType:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        try:
            await self.db.delete(obj)
            await self.db.commit()
            return obj
        except Exception as e:
            if self.setting.DEV_MODE:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                await self.db.rollback()
                raise HTTPException(status_code=500, detail="Có lỗi xảy ra")

    async def save_async(self, obj: ModelType) -> ModelType:
        try:
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            return obj
        except Exception as e:
            if self.setting.DEV_MODE:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                await self.db.rollback()
                raise HTTPException(status_code=500, detail="Có lỗi xảy ra")


class Repository(BaseRepository[ModelType], Generic[ModelType]):
    """
    Base class cho CRUD operations

    Attributes:
        model (Type[ModelType]): SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Khởi tạo CRUD object với model

        Args:
            model (Type[ModelType]): SQLAlchemy model class
        """
        super().__init__(model, db)

    async def create(self, data: ModelType) -> ModelType:
        try:
            self.db.add(data)
            await self.db.commit()
            await self.db.refresh(data)
            return data
        except Exception as e:
            if self.setting.DEV_MODE:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                await self.db.rollback()
                raise HTTPException(status_code=500, detail="Có lỗi xảy ra")

    async def create_async(self, data: ModelType) -> ModelType:
        """
        Tạo object mới

        Args:
            data (CreateSchemaType): Schema dữ liệu đầu vào

        Returns:
            ModelType: Object đã tạo
        """
        try:
            self.db.add(data)
            await self.db.commit()
            await self.db.refresh(data)
            return data
        except Exception as e:
            if self.setting.DEV_MODE:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                await self.db.rollback()
                raise HTTPException(status_code=500, detail="Có lỗi xảy ra")
