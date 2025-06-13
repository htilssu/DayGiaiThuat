from http.client import HTTPException
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.database.database import Base
from app.database.database import SessionLocal
from app.core.config import settings

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.db = SessionLocal()
        self.setting = settings

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def remove(self, *, id: int) -> ModelType:
        obj = self.db.query(self.model).get(id)
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        self.db.delete(obj)
        self.db.commit()
        return obj

    def save(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    async def get_async(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    async def get_multi_async(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    async def remove_async(self, *, id: int) -> ModelType:
        obj = self.db.query(self.model).get(id)
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        try:
            self.db.delete(obj)
            self.db.commit()
            return obj
        except Exception as e:
            if self.setting.DEV_MODE:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                self.db.rollback()
                raise HTTPException(status_code=500, detail="Có lỗi xảy ra")

    async def save_async(self, obj: ModelType) -> ModelType:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception as e:
            if self.setting.DEV_MODE:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                self.db.rollback()
                raise HTTPException(status_code=500, detail="Có lỗi xảy ra")


class Repository(BaseRepository[ModelType], Generic[ModelType]):
    """
    Base class cho CRUD operations

    Attributes:
        model (Type[ModelType]): SQLAlchemy model class
    """

    def __init__(
        self,
        model: Type[ModelType],
    ):
        """
        Khởi tạo CRUD object với model

        Args:
            model (Type[ModelType]): SQLAlchemy model class
        """
        super().__init__(model)

    def create(self, data: ModelType) -> ModelType:
        try:
            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
            return data
        except Exception as e:
            if self.setting.DEV_MODE:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                self.db.rollback()
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
            self.db.commit()
            self.db.refresh(data)
            return data
        except Exception as e:
            if self.setting.DEV_MODE:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                self.db.rollback()
                raise HTTPException(status_code=500, detail="Có lỗi xảy ra")
