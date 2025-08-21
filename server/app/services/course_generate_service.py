import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.agents.course_composition_agent import CourseCompositionAgent
from app.database.database import get_independent_db_session
from app.models import Course, Topic
from app.schemas import CourseCompositionRequestSchema
from app.services.base_generate_service import BaseGenerateService
from app.utils.model_utils import pydantic_to_sqlalchemy_scalar


class CourseGenerateService(BaseGenerateService[Course]):
    async def generate(
            self,
            course_request: CourseCompositionRequestSchema,
            **kwargs,
    ):
        async with get_independent_db_session() as db:
            agent = CourseCompositionAgent()
            [course, _] = await agent.act(course_request)

            topics = [pydantic_to_sqlalchemy_scalar(topic, Topic) for topic in course.topics]

            course_model = await db.execute(
                select(Course).options(selectinload(Course.topics)).where(Course.id == course_request.course_id)
                )
            course_model = course_model.scalar_one()
            course_model.duration = course.duration
            course_model.description = course.description

            for topic in topics:
                course_model.topics.append(topic)

            await db.commit()
            if not course_model:
                raise ValueError(
                    f"Course with ID {course_request.course_id} not found."
                )
            return course_model

    async def background_create(self, composition_request: CourseCompositionRequestSchema):
        asyncio.create_task(self.generate(composition_request))


def get_course_generate_service() -> CourseGenerateService:
    return CourseGenerateService()
