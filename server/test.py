import asyncio

from app.core.agents.lesson_generating_agent import LessonGeneratingAgent
from app.schemas import CourseCompositionRequestSchema
from app.services.course_generate_service import CourseGenerateService
from app.services.lesson_generate_service import LessonGenerateService


async def main():
    course_g = CourseGenerateService()
    course_request = CourseCompositionRequestSchema(
        course_id=256,
        course_title="Cấu trúc dữ liệu và giải thuật",
        course_description="Cấu trúc dữ liệu và giải thuật"
    )
    lesson = LessonGenerateService()

    course = await course_g.generate(course_request)
    await lesson.generate_all_by_topic(course.topics)
    print("Done")


if __name__ == "__main__":
    asyncio.run(main())
