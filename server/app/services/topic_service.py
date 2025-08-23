from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException
from sqlalchemy.orm import selectinload

from app.database.database import get_async_db
from app.models.topic_model import Topic
from app.models.lesson_model import Lesson
from app.schemas.topic_schema import (
    TopicDetailWithProgressResponse,
    TopicWithLesson,
    CreateTopicSchema,
    UpdateTopicSchema,
)
from app.schemas.lesson_schema import LessonWithChildSchema, LessonWithProgressResponse
from app.utils.model_utils import convert_lesson_to_schema
from app.models.user_course_model import UserCourse
from app.models.user_course_progress_model import ProgressStatus, UserCourseProgress


class TopicService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_topic(self, topic_data: CreateTopicSchema) -> TopicWithLesson:
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

        return TopicWithLesson.model_validate(topic)

    async def get_topic_by_id(self, topic_id: int) -> Optional[Topic]:
        """
        Get a topic by ID.
        """
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        topic = result.scalar_one_or_none()

        if not topic:
            return None

        return topic

    async def update_topic(
            self, topic_id: int, topic_data: UpdateTopicSchema
    ) -> TopicWithLesson:
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

        return TopicWithLesson.model_validate(topic)

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

    async def get_topics_by_course_id(self, course_id: int) -> List[TopicWithLesson]:
        """
        Lấy danh sách topics theo course_id
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

        return [TopicWithLesson.model_validate(topic) for topic in topics]

    async def get_topic_with_progress(
            self, topic_id: int, user_id: Optional[int] = None
    ) -> TopicDetailWithProgressResponse:
        """Lấy topic với nested lessons và progress"""
        # Get topic with lessons
        topic = await self.db.execute(
            select(Topic)
            .options(selectinload(Topic.lessons))
            .filter(Topic.id == topic_id)
        )
        topic = topic.scalar_one_or_none()

        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Check enrollment
        user_course_id = None
        if user_id:
            user_course = await self.db.execute(
                select(UserCourse).filter(
                    UserCourse.user_id == user_id,
                    UserCourse.course_id == topic.course_id,
                )
            )
            if user_course:
                user_course_id = user_course.scalar_one_or_none()

        # Get progress map for this topic
        progress_map = {}
        if user_course_id:
            progress_records = await self.db.execute(
                select(UserCourseProgress).filter(
                    UserCourseProgress.user_course_id == user_course_id,
                    UserCourseProgress.topic_id == topic_id,
                )
            )
            progress_records = progress_records.scalars().all()
            # Map progress by lesson_id
            progress_map = {p.lesson_id: p for p in progress_records}

        # Build enhanced lessons
        enhanced_lessons = []
        completed_lessons = 0

        for lesson in sorted(topic.lessons, key=lambda x: x.order):
            progress = progress_map.get(lesson.id)

            lesson_status = ProgressStatus.NOT_STARTED
            lesson_last_viewed = None
            lesson_completed_at = None
            lesson_completion = 0.0

            if progress:
                lesson_status = progress.status
                lesson_last_viewed = progress.updated_at
                lesson_completed_at = (
                    progress.completed_at
                    if progress.status == ProgressStatus.COMPLETED
                    else None
                )
                lesson_completion = (
                    100.0
                    if progress.status == ProgressStatus.COMPLETED
                    else (
                        50.0 if progress.status == ProgressStatus.IN_PROGRESS else 0.0
                    )
                )

                if lesson_status == ProgressStatus.COMPLETED:
                    completed_lessons += 1

            enhanced_lessons.append(
                LessonWithProgressResponse(
                    id=lesson.id,
                    external_id=lesson.external_id,
                    title=lesson.title,
                    description=lesson.description,
                    order=lesson.order,
                    next_lesson_id=None,
                    prev_lesson_id=None,
                    status=lesson_status,
                    last_viewed_at=lesson_last_viewed,
                    completed_at=lesson_completed_at,
                    completion_percentage=lesson_completion,
                )
            )

        # Calculate topic completion percentage
        total_lessons = len(enhanced_lessons)
        topic_completion_percentage = (
            (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
        )

        return TopicDetailWithProgressResponse(
            id=topic.id,
            name=topic.name,
            description=topic.description,
            order=topic.order,
            course_id=topic.course_id,
            lessons=enhanced_lessons,
            topic_completion_percentage=round(topic_completion_percentage, 2),
            completed_lessons=completed_lessons,
            total_lessons=total_lessons,
            user_course_id=user_course_id.id if user_course_id else None,
        )

    async def get_next_topic(self, current_topic_id: int) -> Optional[Topic]:
        current_topic = await self.db.get(Topic, current_topic_id)
        if not current_topic:
            return None

        next_topic_stmt = (
            select(Topic)
            .where(
                Topic.course_id == current_topic.course_id,
                Topic.order == current_topic.order + 1,
            )
            .limit(1)
        )
        next_topic = (await self.db.execute(next_topic_stmt)).scalar_one_or_none()
        return next_topic

    async def get_lessons_by_topic_id(
            self, topic_id: int
    ) -> List[LessonWithChildSchema]:
        stmt = (
            select(Lesson)
            .where(Lesson.topic_id == topic_id)
            .options(selectinload(Lesson.sections), selectinload(Lesson.exercises))
            .order_by(Lesson.order)
        )
        result = await self.db.execute(stmt)
        lessons = result.scalars().all()

        return [convert_lesson_to_schema(lesson) for lesson in lessons]


def get_topic_service(db: AsyncSession = Depends(get_async_db)) -> TopicService:
    return TopicService(db)
