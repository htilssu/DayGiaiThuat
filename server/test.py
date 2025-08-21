import asyncio

from app.schemas import CourseCompositionRequestSchema
from app.services.course_generate_service import CourseGenerateService


async def main():
    course_g = CourseGenerateService()
    course_request = CourseCompositionRequestSchema(
        course_id=251,
        course_title="Cấu trúc dữ liệu và giải thuật",
        course_description="Cấu trúc dữ liệu và giải thuật"
    )

    course = await course_g.generate(course_request)

    print("Done")


if __name__ == "__main__":
    asyncio.run(main())
