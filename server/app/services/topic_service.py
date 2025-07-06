from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload

from app.database.database import get_async_db
from app.models.topic_model import Topic
from app.schemas.topic_schema import (
    CreateTopicSchema,
    UpdateTopicSchema,
    TopicResponse,
)


class TopicService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_topic_by_id(self, topic_id: int) -> Optional[TopicResponse]:
        """
        Get a topic by ID.
        """
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        topic = result.scalar_one_or_none()

        if not topic:
            return None

        return TopicResponse.model_validate(topic)


def get_topic_service(db: AsyncSession = Depends(get_async_db)) -> TopicService:
    """
    Dependency injection for TopicService

    Args:
        db: Async database session

    Returns:
        TopicService: Service instance
    """
    return TopicService(db)