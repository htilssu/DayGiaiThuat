import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.agents.course_composition_agent import CourseCompositionAgent
from app.database.database import get_independent_db_session
from app.models import Course, Topic
from app.schemas import CourseCompositionRequestSchema
from app.services.base_generate_service import BaseGenerateService
from app.services.lesson_generate_service import LessonGenerateService
from app.utils.model_utils import pydantic_to_sqlalchemy_scalar


class CourseGenerateService(BaseGenerateService[Course]):
    async def generate(
        self,
        course_request: CourseCompositionRequestSchema,
        **kwargs,
    ):
        async with get_independent_db_session() as db:
            agent = CourseCompositionAgent()
            [course_schema, _] = await agent.act(course_request)

            topics = [
                pydantic_to_sqlalchemy_scalar(topic, Topic)
                for topic in course_schema.topics
            ]

            result = await db.execute(
                select(Course)
                .options(selectinload(Course.topics))
                .where(Course.id == course_request.course_id)
            )
            course: Course = result.scalar_one()
            if not course:
                raise ValueError(
                    f"Course with ID {course_request.course_id} not found."
                )

            course.duration = course_schema.duration
            course.description = course_schema.description
            course.topics.clear()
            await db.flush()

            for topic in topics:
                course.topics.append(topic)

            await db.commit()
            if not course:
                raise ValueError(
                    f"Course with ID {course_request.course_id} not found."
                )
            await db.refresh(course)

            lesson_generate_service = LessonGenerateService()
            await lesson_generate_service.generate_all_by_topic(course.topics)

            return course

    async def background_create(
        self, composition_request: CourseCompositionRequestSchema
    ):
        asyncio.create_task(self.generate(composition_request))


def get_course_generate_service() -> CourseGenerateService:
    return CourseGenerateService()
