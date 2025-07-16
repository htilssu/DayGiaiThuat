from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends
from sqlalchemy.orm import selectinload
import uuid
from fastapi import HTTPException, status

from app.database.database import get_async_db
from app.models.lesson_model import Lesson, LessonSection
from app.models.lesson_generation_state_model import LessonGenerationState
from app.models.user_course_model import UserCourse
from app.schemas.lesson_schema import (
    CreateLessonSchema,
    LessonDetailWithProgressResponse,
    UpdateLessonSchema,
    LessonWithChildSchema,
    GenerateLessonRequestSchema,
    LessonCompleteResponseSchema,
    LessonSectionSchema,
)
from app.core.agents.lesson_generating_agent import get_lesson_generating_agent
from app.utils.model_utils import convert_lesson_to_schema


from app.services.topic_service import get_topic_service, TopicService
from app.models.user_course_progress_model import ProgressStatus, UserCourseProgress
from app.models.topic_model import Topic
from datetime import datetime


class LessonService:
    def __init__(self, db: AsyncSession, topic_service: TopicService):
        self.db = db
        self.agent = get_lesson_generating_agent()
        self.topic_service = topic_service

    async def generate_lesson(
        self, request: GenerateLessonRequestSchema, topic_id: int, order: int
    ) -> Optional[LessonWithChildSchema]:
        """
        Generate a lesson using the RAG AI agent and log the state.
        """
        # Validate topic
        topic = await self.topic_service.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        if not request.session_id:
            request.session_id = str(uuid.uuid4())

        # Create initial state
        generation_state = LessonGenerationState(
            session_id=request.session_id,
            topic_id=topic_id,
            status="in_progress",
            request_data=request.model_dump_json(),
        )
        self.db.add(generation_state)
        await self.db.commit()
        await self.db.refresh(generation_state)

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

            # Update state to completed
            generation_state.status = "completed"  # type: ignore
            generation_state.lesson_id = created_lessons[0].id if created_lessons else None  # type: ignore # Link to the first created lesson
            await self.db.commit()

            return (
                created_lessons[0] if created_lessons else None
            )  # Return the first created lesson

        except Exception as e:
            # Update state to failed
            generation_state.status = "failed"  # type: ignore
            await self.db.commit()
            # Re-raise the exception
            raise e

    async def create_lesson(
        self, lesson_data: CreateLessonSchema
    ) -> LessonWithChildSchema:
        """
        Create a new lesson with sections.
        """
        # Create lesson
        lesson = Lesson(
            external_id=lesson_data.external_id,
            title=lesson_data.title,
            description=lesson_data.description,
            topic_id=lesson_data.topic_id,
            order=lesson_data.order,
            next_lesson_id=lesson_data.next_lesson_id,
            prev_lesson_id=lesson_data.prev_lesson_id,
        )

        self.db.add(lesson)
        await self.db.flush()  # Get the lesson ID

        # Create lesson sections
        for section_data in lesson_data.sections:
            # Chuyển đổi options từ Pydantic model sang dict nếu tồn tại
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

        # Tải rõ ràng các mối quan hệ trước khi chuyển đổi
        await self.db.refresh(lesson, ["sections", "exercises"])

        # Sử dụng hàm tiện ích để chuyển đổi từ model sang schema
        return convert_lesson_to_schema(lesson)

    async def get_lesson_by_id(self, lesson_id: int) -> Optional[LessonWithChildSchema]:
        """
        Get a lesson by ID.
        """
        stmt = (
            select(Lesson)
            .where(Lesson.id == lesson_id)
            .options(selectinload(Lesson.sections), selectinload(Lesson.exercises))
        )
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        # Sử dụng hàm tiện ích để chuyển đổi từ model sang schema
        return convert_lesson_to_schema(lesson)

    async def get_lesson_by_order(
        self, topic_id: int, order: int
    ) -> Optional[LessonWithChildSchema]:
        """
        Get a lesson by order.
        """
        stmt = select(Lesson).where(Lesson.topic_id == topic_id, Lesson.order == order)
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        # Sử dụng hàm tiện ích để chuyển đổi từ model sang schema
        return convert_lesson_to_schema(lesson)

    async def get_lesson_by_external_id(
        self, external_id: str
    ) -> Optional[LessonWithChildSchema]:
        """
        Get a lesson by external ID.
        """
        stmt = (
            select(Lesson)
            .where(Lesson.external_id == external_id)
            .options(selectinload(Lesson.sections), selectinload(Lesson.exercises))
        )
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        # Sử dụng hàm tiện ích để chuyển đổi từ model sang schema
        return convert_lesson_to_schema(lesson)

    async def get_lessons_by_topic(self, topic_id: int) -> List[LessonWithChildSchema]:
        """
        Get all lessons for a topic.
        """
        stmt = (
            select(Lesson)
            .where(Lesson.topic_id == topic_id)
            .order_by(Lesson.order)
            .options(selectinload(Lesson.sections), selectinload(Lesson.exercises))
        )
        result = await self.db.execute(stmt)
        lessons = result.scalars().all()

        # Sử dụng hàm tiện ích để chuyển đổi từ model sang schema
        return [convert_lesson_to_schema(lesson) for lesson in lessons]

    async def complete_lesson(
        self, lesson_id: int, user_id: int
    ) -> LessonCompleteResponseSchema:
        # Lấy bài học hiện tại
        current_lesson = await self.db.execute(
            select(Lesson)
            .options(selectinload(Lesson.topic))
            .where(Lesson.id == lesson_id)
        )
        current_lesson = current_lesson.scalar_one_or_none()
        if not current_lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        # Tìm bài học tiếp theo trong cùng một chủ đề
        next_lesson_stmt = (
            select(Lesson)
            .where(
                Lesson.topic_id == current_lesson.topic_id,
                Lesson.order == current_lesson.order + 1,
            )
            .limit(1)
        )
        next_lesson = (await self.db.execute(next_lesson_stmt)).scalar_one_or_none()
        user_course = await self.db.execute(
            select(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.course_id == current_lesson.topic.course_id,
            )
        )
        user_course = user_course.scalar_one_or_none()
        if user_course is None:
            raise HTTPException(status_code=404, detail="User state not found")

        # Lưu thông tin hoàn thành bài học vào UserCourseProgress
        progress_stmt = select(UserCourseProgress).where(
            UserCourseProgress.user_course_id == user_course.id,
            UserCourseProgress.topic_id == current_lesson.topic_id,
            UserCourseProgress.lesson_id == lesson_id,
        )
        progress = (await self.db.execute(progress_stmt)).scalar_one_or_none()
        if progress:
            progress.status = ProgressStatus.COMPLETED
            progress.completed_at = datetime.now()
        else:
            progress = UserCourseProgress(
                user_course_id=user_course.id,
                topic_id=current_lesson.topic_id,
                lesson_id=lesson_id,
                status=ProgressStatus.COMPLETED,
                completed_at=datetime.utcnow(),
            )
            self.db.add(progress)
        await self.db.commit()

        if next_lesson:
            # Nếu có bài học tiếp theo, cập nhật trạng thái người dùng
            user_course.current_lesson = next_lesson.id
            user_course.current_topic = next_lesson.topic_id
            await self.db.commit()
            return LessonCompleteResponseSchema(
                lesson_id=next_lesson.id,
                next_lesson_id=next_lesson.id,
                is_completed=True,
            )
        else:
            # Nếu không có bài học tiếp theo, tìm chủ đề tiếp theo
            topic = await self.topic_service.get_next_topic(current_lesson.topic_id)
            if topic:
                # Tìm bài học đầu tiên của chủ đề tiếp theo
                first_lesson_stmt = (
                    select(Lesson)
                    .where(Lesson.topic_id == topic.id)
                    .order_by(Lesson.order)
                    .limit(1)
                )
                first_lesson_of_next_topic = (
                    await self.db.execute(first_lesson_stmt)
                ).scalar_one_or_none()

                if first_lesson_of_next_topic:
                    user_course.current_lesson = first_lesson_of_next_topic.id
                    user_course.current_topic = first_lesson_of_next_topic.topic_id
                    await self.db.commit()
                    return LessonCompleteResponseSchema(
                        lesson_id=first_lesson_of_next_topic.id,
                        next_lesson_id=first_lesson_of_next_topic.id,
                        is_completed=True,
                    )
        # Nếu không có bài học tiếp theo hoặc chủ đề tiếp theo
        return LessonCompleteResponseSchema(
            lesson_id=lesson_id, next_lesson_id=None, is_completed=True
        )

    async def update_lesson(
        self, lesson_id: int, lesson_data: UpdateLessonSchema
    ) -> Optional[LessonWithChildSchema]:
        """
        Update a lesson.
        """
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        # Update fields
        for field, value in lesson_data.model_dump(exclude_unset=True).items():
            setattr(lesson, field, value)

        await self.db.commit()
        await self.db.refresh(lesson)

        # Tải rõ ràng các mối quan hệ
        await self.db.refresh(lesson, ["sections", "exercises"])

        # Sử dụng hàm tiện ích để chuyển đổi từ model sang schema
        return convert_lesson_to_schema(lesson)

    async def mark_lesson_completed(self, lesson_id: int, user_id: int):
        """
        Mark a lesson as completed.
        """
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return False

        # lesson.is_completed = True
        await self.db.commit()

    async def delete_lesson(self, lesson_id: int) -> bool:
        """
        Delete a lesson.
        """
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
    ) -> LessonDetailWithProgressResponse:
        """Lấy lesson với progress"""
        lesson = await self.db.execute(
            select(Lesson)
            .filter(Lesson.id == lesson_id)
            .options(selectinload(Lesson.sections))
        )
        lesson = lesson.scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        # Get topic and course info
        topic = await self.db.execute(select(Topic).filter(Topic.id == lesson.topic_id))
        topic = topic.scalar_one_or_none()

        # Check enrollment
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

        # Get progress for this lesson
        lesson_status = ProgressStatus.NOT_STARTED
        lesson_last_viewed = None
        lesson_completed_at = None
        lesson_completion = 0.0

        if user_course_id:
            progress = await self.db.execute(
                select(UserCourseProgress).filter(
                    UserCourseProgress.user_course_id == user_course_id,
                    UserCourseProgress.topic_id == lesson.topic_id,
                    UserCourseProgress.lesson_id == lesson_id,
                )
            )
            progress = progress.scalar_one_or_none()

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

        return LessonDetailWithProgressResponse(
            id=lesson.id,
            external_id=lesson.external_id,
            title=lesson.title,
            description=lesson.description,
            order=lesson.order,
            topic_id=lesson.topic_id,
            sections=(
                [
                    LessonSectionSchema(
                        type=section.type,
                        content=section.content,
                        order=section.order,
                        options=section.options,
                        answer=section.answer,
                        explanation=section.explanation,
                    )
                    for section in lesson.sections
                ]
                if lesson.sections
                else []
            ),
            status=lesson_status,
            last_viewed_at=lesson_last_viewed,
            completed_at=lesson_completed_at,
            completion_percentage=lesson_completion,
            user_course_id=user_course_id,
        )


def get_lesson_service(
    db: AsyncSession = Depends(get_async_db),
    topic_service: TopicService = Depends(get_topic_service),
) -> LessonService:
    """
    Dependency injection for LessonService

    Args:
        db: Async database session
        topic_service: Topic service instance

    Returns:
        LessonService: Service instance
    """
    return LessonService(db=db, topic_service=topic_service)
