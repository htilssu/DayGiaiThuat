import asyncio

from app.core.agents.course_composition_agent import CourseCompositionAgent
from app.database.database import get_independent_db_session
from app.models import Course
from app.schemas import CourseCompositionRequestSchema
from app.services.base_generate_service import BaseGenerateService
from app.services.course_daft_service import update_or_create_course_draft


class CourseGenerateService(BaseGenerateService[Course]):
    async def generate(
            self,
            course_request: CourseCompositionRequestSchema,
            **kwargs,
    ):
        async with get_independent_db_session() as db:
            agent = CourseCompositionAgent(db)
            [course, _] = await agent.act(course_request)
            course.course_id = course_request.course_id

            update_or_create_course_draft(course_request.course_id, course_draft=course)

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
