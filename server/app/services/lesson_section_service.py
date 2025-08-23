from typing import List

from sqlalchemy import select

from app.database.database import get_independent_db_session
from app.models.lesson_model import LessonSection


async def get_sections_by_lesson(lesson_id: int) -> List[LessonSection]:
    async with get_independent_db_session() as db:
        result = await db.execute(
            select(LessonSection).where(LessonSection.lesson_id == lesson_id).order_by(LessonSection.order)
        )
        return result.scalars().all()
