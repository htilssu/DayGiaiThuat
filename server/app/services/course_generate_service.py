import asyncio

from sqlalchemy import update

from app.core.agents.course_composition_agent import CourseCompositionAgent
from app.database.database import get_independent_db_session
from app.models import Course
from app.schemas import CourseCompositionRequestSchema
from app.services.base_generate_service import BaseGenerateService


class CourseGenerateService(BaseGenerateService[Course]):
    async def generate(
            self,
            course_request: CourseCompositionRequestSchema,
            **kwargs,
    ):
        async with get_independent_db_session() as db:
            agent = CourseCompositionAgent(db)
            [course, session_id] = await agent.act(course_request)
            await db.execute(
                update(Course)
                .where(Course.id == course_request.course_id)
                .values(
                    duration=course.duration,
                    description=course.description,
                )
            )
            await db.commit()
            course_model = await db.get(Course, course_request.course_id)
            if not course_model:
                raise ValueError(
                    f"Course with ID {course_request.course_id} not found."
                )
            return course_model

    async def background_create(self, composition_request: CourseCompositionRequestSchema):
        asyncio.create_task(self.generate(composition_request))


def get_course_generate_service() -> BaseGenerateService[Course]:
    return CourseGenerateService()
