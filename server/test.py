import asyncio
import uuid

from sqlalchemy import select

from app.database.database import get_independent_db_session
from app.models import Topic
from app.services.lesson_generate_service import LessonGenerateService


async def main():
    async with get_independent_db_session() as db:
        topic_list = (await db.execute(select(Topic).filter(Topic.course_id == 236))).scalars().all()
        await LessonGenerateService().generate_all_by_topic(topic_list=topic_list, session_id=uuid.uuid4().hex)


if __name__ == "__main__":
    asyncio.run(main())
