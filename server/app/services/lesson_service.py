import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.agents.lesson_generating_agent import (
    get_lesson_generating_agent,
)
from app.database.database import get_async_db
from app.models.lesson_model import Lesson, LessonSection
from app.models.topic_model import Topic
from app.models.user_course_model import UserCourse
from app.models.user_lesson_model import UserLesson
from sqlalchemy import func
from app.schemas.lesson_schema import (
    CreateLessonSchema,
    UpdateLessonSchema,
    LessonWithChildSchema,
    GenerateLessonRequestSchema,
    LessonCompleteResponseSchema,
)
from app.services.topic_service import get_topic_service, TopicService
from app.services.profile_service import ProfileService
from app.models.user_activity_model import ActivityType
from app.utils.model_utils import convert_lesson_to_schema


class LessonService:
    def __init__(self, db: AsyncSession, topic_service: TopicService):
        self.db = db
        self.agent = get_lesson_generating_agent()
        self.topic_service = topic_service
        self.profile_service = ProfileService(db)

    async def generate_lesson(
        self, request: GenerateLessonRequestSchema, topic_id: int, order: int
    ) -> Optional[LessonWithChildSchema]:
        topic = await self.topic_service.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        if not request.session_id:
            request.session_id = str(uuid.uuid4())

        await self.db.commit()

        try:
            # Generate lesson using the agent
            list_lesson_data = await self.agent.act(**request.model_dump())

            # Create the lessons in database
            created_lessons = []
            for lesson_data in list_lesson_data:
                lesson_data.topic_id = topic_id
                lesson_data.order = order  # This might need adjustment if agent returns multiple lessons with their own intended order
                lesson = await self.create_lesson(lesson_data)
                created_lessons.append(lesson)

            await self.db.commit()

            return created_lessons[0] if created_lessons else None

        except Exception as e:
            await self.db.commit()
            raise e

    async def create_lesson(
        self, lesson_data: CreateLessonSchema
    ) -> LessonWithChildSchema:
        lesson = Lesson(
            title=lesson_data.title,
            description=lesson_data.description,
            topic_id=lesson_data.topic_id,
            order=lesson_data.order,
        )

        self.db.add(lesson)
        await self.db.commit()

        for section_data in lesson_data.sections:
            options_dict = None
            if section_data.options:
                options_dict = section_data.options.model_dump()

            section = LessonSection(
                lesson_id=lesson.id,
                type=section_data.type,
                content=section_data.content,
                order=section_data.order,
                options=options_dict,
                answer=section_data.answer,
                explanation=section_data.explanation,
            )
            self.db.add(section)

        await self.db.commit()
        await self.db.refresh(lesson)

        await self.db.refresh(lesson, ["sections", "exercises"])

    async def get_lesson_by_id(self, lesson_id: int) -> Optional[LessonWithChildSchema]:
        stmt = (
            select(Lesson)
            .where(Lesson.id == lesson_id)
            .options(selectinload(Lesson.sections))
        )
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        return convert_lesson_to_schema(lesson)

    async def get_lesson_by_order(
        self, topic_id: int, order: int
    ) -> Optional[LessonWithChildSchema]:
        stmt = select(Lesson).where(Lesson.topic_id == topic_id, Lesson.order == order)
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        return convert_lesson_to_schema(lesson)

    async def get_lessons_by_topic(self, topic_id: int) -> List[LessonWithChildSchema]:
        stmt = (
            select(Lesson)
            .where(Lesson.topic_id == topic_id)
            .order_by(Lesson.order)
            .options(selectinload(Lesson.sections))
        )
        result = await self.db.execute(stmt)
        lessons = result.scalars().all()

        return [convert_lesson_to_schema(lesson) for lesson in lessons]

    async def get_next_lesson(self, lesson: Lesson) -> Optional[Lesson]:
        next_lesson_stmt = (
            select(Lesson)
            .where(
                Lesson.topic_id == lesson.topic_id,
                Lesson.order == lesson.order + 1,
            )
            .limit(1)
        )
        next_lesson = (await self.db.execute(next_lesson_stmt)).scalar_one_or_none()
        if not next_lesson:
            next_topic: Topic | None = (
                await self.db.execute(
                    select(Topic)
                    .where(
                        Topic.order > lesson.topic.order,
                        Topic.course_id == lesson.topic.course_id,
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
            if next_topic:
                next_lesson = (
                    await self.db.execute(
                        select(Lesson)
                        .filter(Lesson.topic_id == next_topic.id)
                        .order_by(Lesson.order)
                        .limit(1)
                    )
                ).scalar_one()
            else:
                next_lesson = None

        return next_lesson

    async def complete_lesson(
        self, lesson_id: int, user_id: int
    ) -> LessonCompleteResponseSchema:
        current_lesson = await self.db.execute(
            select(Lesson)
            .options(selectinload(Lesson.topic))
            .where(Lesson.id == lesson_id)
        )
        current_lesson = current_lesson.scalar_one_or_none()
        if not current_lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        user_course = await self.db.execute(
            select(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.course_id == current_lesson.topic.course_id,
            )
        )
        user_course = user_course.scalar_one_or_none()
        if user_course is None:
            raise HTTPException(status_code=404, detail="User state not found")

        progress_stmt = select(UserLesson).where(
            UserLesson.user_id == user_id,
            UserLesson.lesson_id == lesson_id,
        )
        progress = (await self.db.execute(progress_stmt)).scalar_one_or_none()
        if progress:
            progress.completed_at = datetime.now()
        else:
            progress = UserLesson(
                lesson_id=lesson_id,
                user_id=user_id,
                completed_at=datetime.now(),
            )
            self.db.add(progress)
        await self.db.commit()

        # Add user activity tracking for lesson completion
        await self.profile_service.add_user_activity(
            user_id=user_id,
            activity_type=ActivityType.LESSON,
            activity_name=f"Hoàn thành bài học: {current_lesson.title}",
            description=f"Đã hoàn thành bài học '{current_lesson.title}' trong chủ đề '{current_lesson.topic.name}'",
            progress="100%",
            related_id=lesson_id,
        )

        # Update topic progress after lesson completion
        await self._update_topic_progress_after_lesson(
            user_id, current_lesson.topic_id, user_course.id
        )

        next_lesson = await self.get_next_lesson(current_lesson)

        if next_lesson:
            user_course.current_lesson = next_lesson.id
            user_course.current_topic = next_lesson.topic_id
            await self.db.commit()
            return LessonCompleteResponseSchema(
                lesson_id=next_lesson.id,
                next_lesson_id=next_lesson.id,
                is_completed=True,
            )
        else:
            return LessonCompleteResponseSchema(
                lesson_id=None,
                next_lesson_id=None,
                is_completed=True,
            )

    async def update_lesson(
        self, lesson_id: int, lesson_data: UpdateLessonSchema
    ) -> Optional[LessonWithChildSchema]:
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        for field, value in lesson_data.model_dump(exclude_unset=True).items():
            setattr(lesson, field, value)

        await self.db.commit()
        await self.db.refresh(lesson)

        await self.db.refresh(lesson, ["sections", "exercises"])

        return convert_lesson_to_schema(lesson)

    async def delete_lesson(self, lesson_id: int) -> bool:
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return False

        await self.db.delete(lesson)
        await self.db.commit()

        return True

    async def get_lesson_with_progress(
        self, lesson_id: int, user_id: Optional[int] = None
    ) -> LessonWithChildSchema:
        lesson = await self.db.execute(
            select(Lesson)
            .filter(Lesson.id == lesson_id)
            .options(selectinload(Lesson.sections))
        )
        lesson = lesson.scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        topic = await self.db.execute(select(Topic).filter(Topic.id == lesson.topic_id))
        topic = topic.scalar_one_or_none()

        user_course_id = None
        if user_id and topic:
            user_course = await self.db.execute(
                select(UserCourse).filter(
                    UserCourse.user_id == user_id,
                    UserCourse.course_id == topic.course_id,
                )
            )
            user_course = user_course.scalar_one_or_none()
            if user_course:
                user_course_id = user_course.id

        if user_course_id:
            progress = await self.db.execute(
                select(UserLesson).filter(
                    UserLesson.user_id == user_id,
                    UserLesson.lesson_id == lesson_id,
                )
            )
            progress = progress.scalar_one_or_none()

        res = LessonWithChildSchema.model_validate(lesson)
        return res

    async def _update_topic_progress_after_lesson(
        self, user_id: int, topic_id: int, user_course_id: int
    ) -> None:
        """
        Cập nhật tiến độ chủ đề sau khi hoàn thành bài học
        """
        # Đếm tổng số bài học trong chủ đề
        total_lessons_result = await self.db.execute(
            select(func.count(Lesson.id)).where(Lesson.topic_id == topic_id)
        )
        total_lessons = total_lessons_result.scalar() or 0

        # Đếm số bài học đã hoàn thành
        completed_lessons_result = await self.db.execute(
            select(func.count(UserLesson.id))
            .join(Lesson, Lesson.id == UserLesson.lesson_id)
            .where(
                UserLesson.user_id == user_id,
                Lesson.topic_id == topic_id,
                UserLesson.completed_at.isnot(None),
            )
        )
        completed_lessons = completed_lessons_result.scalar() or 0

        # Tính phần trăm hoàn thành
        if total_lessons > 0:
            progress_percentage = (completed_lessons / total_lessons) * 100
        else:
            progress_percentage = 0

        # Cập nhật UserTopicProgress
        await self.profile_service.update_topic_progress(
            user_id=user_id,
            topic_id=topic_id,
            progress_percentage=progress_percentage,
            lessons_completed=completed_lessons,
        )


def get_lesson_service(
    db: AsyncSession = Depends(get_async_db),
    topic_service: TopicService = Depends(get_topic_service),
) -> LessonService:
    return LessonService(db=db, topic_service=topic_service)
