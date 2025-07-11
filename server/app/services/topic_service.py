from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException
from sqlalchemy.orm import selectinload

from app.database.database import get_async_db
from app.models.topic_model import Topic
from app.models.lesson_model import Lesson
from app.schemas.topic_schema import (
    TopicResponse,
    TopicWithLessonsResponse,
    CreateTopicSchema,
    UpdateTopicSchema,
)
from app.schemas.lesson_schema import LessonResponseSchema
from app.utils.model_utils import convert_lesson_to_schema


class TopicService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_topic(self, topic_data: CreateTopicSchema) -> TopicResponse:
        """
        Tạo topic mới
        """
        topic = Topic(
            name=topic_data.name,
            description=topic_data.description,
            prerequisites=topic_data.prerequisites,
            course_id=topic_data.course_id,
            external_id=topic_data.external_id,
        )

        self.db.add(topic)
        await self.db.commit()
        await self.db.refresh(topic)

        return TopicResponse.model_validate(topic)

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

    async def update_topic(
        self, topic_id: int, topic_data: UpdateTopicSchema
    ) -> TopicResponse:
        """
        Cập nhật topic
        """
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        topic = result.scalar_one_or_none()

        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Cập nhật các trường nếu được cung cấp
        if topic_data.name is not None:
            topic.name = topic_data.name
        if topic_data.description is not None:
            topic.description = topic_data.description
        if topic_data.prerequisites is not None:
            topic.prerequisites = topic_data.prerequisites
        if topic_data.external_id is not None:
            topic.external_id = topic_data.external_id

        await self.db.commit()
        await self.db.refresh(topic)

        return TopicResponse.model_validate(topic)

    async def delete_topic(self, topic_id: int) -> None:
        """
        Xóa topic
        """
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        topic = result.scalar_one_or_none()

        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        await self.db.delete(topic)
        await self.db.commit()

    async def get_topics_by_course_id(self, course_id: int) -> List[TopicResponse]:
        """
        Lấy danh sách topics theo course_id
        """
        stmt = (
            select(Topic)
            .where(Topic.course_id == course_id)
            .order_by(Topic.order.asc().nulls_last(), Topic.id.asc())
        )

        result = await self.db.execute(stmt)
        topics = result.scalars().all()

        return [TopicResponse.model_validate(topic) for topic in topics]

    async def get_lessons_by_topic_id(
        self, topic_id: int
    ) -> List[LessonResponseSchema]:
        """
        Lấy danh sách lessons theo topic_id
        """
        stmt = (
            select(Lesson)
            .where(Lesson.topic_id == topic_id)
            .options(selectinload(Lesson.sections), selectinload(Lesson.exercises))
            .order_by(Lesson.order)
        )
        result = await self.db.execute(stmt)
        lessons = result.scalars().all()

        return [convert_lesson_to_schema(lesson) for lesson in lessons]

    async def get_topic_with_lessons(
        self, topic_id: int
    ) -> Optional[TopicWithLessonsResponse]:
        """
        Lấy một topic cụ thể cùng với lessons của nó

        Args:
            topic_id: ID của topic

        Returns:
            TopicWithLessonsResponse: Topic cùng với lessons hoặc None nếu không tìm thấy
        """
        stmt = (
            select(Topic)
            .where(Topic.id == topic_id)
            .options(
                selectinload(Topic.lessons).selectinload(Lesson.sections),
                selectinload(Topic.lessons).selectinload(Lesson.exercises),
            )
        )

        result = await self.db.execute(stmt)
        topic = result.scalar_one_or_none()

        if not topic:
            return None

        # Convert lessons manually to ensure proper schema conversion
        lessons_schemas = [convert_lesson_to_schema(lesson) for lesson in topic.lessons]

        # Create the response manually to avoid Pydantic validation issues
        return TopicWithLessonsResponse(
            id=topic.id,
            external_id=topic.external_id,
            course_id=topic.course_id,
            name=topic.name,
            description=topic.description,
            prerequisites=topic.prerequisites,
            order=topic.order,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
            lessons=lessons_schemas,
        )

    async def get_topics_with_lessons_by_course_id(
        self, course_id: int
    ) -> List[TopicWithLessonsResponse]:
        """
        Lấy tất cả topics cùng với lessons theo course_id

        Args:
            course_id: ID của khóa học

        Returns:
            List[TopicWithLessonsResponse]: Danh sách topics cùng với lessons
        """
        stmt = (
            select(Topic)
            .where(Topic.course_id == course_id)
            .options(
                selectinload(Topic.lessons).selectinload(Lesson.sections),
                selectinload(Topic.lessons).selectinload(Lesson.exercises),
            )
            .order_by(Topic.order.asc().nulls_last(), Topic.id.asc())
        )

        result = await self.db.execute(stmt)
        topics = result.scalars().all()

        # Convert each topic manually to ensure proper schema conversion
        topics_responses = []
        for topic in topics:
            lessons_schemas = [
                convert_lesson_to_schema(lesson) for lesson in topic.lessons
            ]

            topic_response = TopicWithLessonsResponse(
                id=topic.id,
                external_id=topic.external_id,
                course_id=topic.course_id,
                name=topic.name,
                description=topic.description,
                prerequisites=topic.prerequisites,
                order=topic.order,
                created_at=topic.created_at,
                updated_at=topic.updated_at,
                lessons=lessons_schemas,
            )
            topics_responses.append(topic_response)

        return topics_responses


def get_topic_service(db: AsyncSession = Depends(get_async_db)) -> TopicService:
    """
    Dependency injection for TopicService

    Args:
        db: Async database session

    Returns:
        TopicService: Service instance
    """
    return TopicService(db)
