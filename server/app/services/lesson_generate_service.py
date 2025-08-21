import asyncio
import uuid
from typing import List

from sqlalchemy.exc import SQLAlchemyError

from app.core.agents.lesson_generating_agent import get_lesson_generating_agent, LessonGeneratingAgent
from app.database.database import get_independent_db_session
from app.models import Topic, Lesson, Exercise
from app.models.lesson_model import LessonSection
from app.services.base_generate_service import BaseGenerateService, T
from app.utils.model_utils import model_to_dict, pydantic_to_sqlalchemy_scalar


class LessonGenerateService(BaseGenerateService[List[Lesson]]):

    async def generate(self, topic: Topic, session_id: str) -> List[Lesson]:
        lesson_generate_agent = LessonGeneratingAgent()
        created_lesson_schema = await lesson_generate_agent.act(
            topic=topic, session_id=session_id
        )
        lesson_list = []
        for lesson_item in created_lesson_schema:
            lesson_model = pydantic_to_sqlalchemy_scalar(lesson_item, Lesson)
            lesson_model.id = None
            lesson_model.topic_id = topic.id
            section = []
            for section_item in lesson_item.sections:
                section_model = pydantic_to_sqlalchemy_scalar(section_item, LessonSection)
                section_model.id = None
                section_model.lesson_id = None  # Set to None to allow SQLAlchemy to generate a new ID
                section.append(section_model)
            lesson_model.sections = section
            lesson_model.exercises = [
                pydantic_to_sqlalchemy_scalar(exercise, Exercise)
                for exercise in lesson_item.exercises
            ]
            lesson_list.append(lesson_model)

        return lesson_list

    async def generate_all_by_topic(self, topic_list: List[Topic]):
        async def process_topic(topic):
            try:
                session_id = uuid.uuid4().hex
                lesson = await self.generate(topic=topic, session_id=session_id)

                for lesson_item in lesson:
                    lesson_item.id = None
                    lesson_item.topic_id = topic.id

                async with get_independent_db_session() as db:
                    db.add_all(lesson)
                    await db.commit()
                    return True
            except Exception as err:
                print(f"Error topic {topic.id}: {err}")
                return False

        tasks = [process_topic(topic) for topic in topic_list]
        results = await asyncio.gather(*tasks)

        success_count = sum(results)
        print(f"Completed: {success_count}/{len(topic_list)}")
