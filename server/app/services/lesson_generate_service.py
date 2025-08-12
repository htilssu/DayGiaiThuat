import uuid
from typing import List

from sqlalchemy.exc import SQLAlchemyError

from app.core.agents.lesson_generating_agent import get_lesson_generating_agent
from app.database.database import get_independent_db_session
from app.models import Topic, Lesson, Exercise
from app.models.lesson_model import LessonSection
from app.services.base_generate_service import BaseGenerateService, T
from app.utils.model_utils import model_to_dict, pydantic_to_sqlalchemy_scalar


class LessonGenerateService(BaseGenerateService[List[Lesson]]):

    async def generate(self, topic: Topic, session_id: str) -> T:
        lesson_generate_agent = get_lesson_generating_agent()
        created_lesson_schema = await lesson_generate_agent.act(topic=topic, session_id=session_id)
        lesson_list = []
        for lesson_item in created_lesson_schema:
            lesson_model = pydantic_to_sqlalchemy_scalar(lesson_item, Lesson)
            lesson_model.id = None
            lesson_model.topic_id = topic.id
            lesson_model.sections = [pydantic_to_sqlalchemy_scalar(section, LessonSection) for section in
                                     lesson_item.sections]
            lesson_model.exercises = [pydantic_to_sqlalchemy_scalar(exercise, Exercise) for exercise in
                                      lesson_item.exercises]
            lesson_list.append(lesson_model)

        return lesson_list

    async def generate_all_by_topic(self, topic_list: List[Topic]):
        for topic in topic_list:
            session_id = uuid.uuid4().hex
            lesson = await self.generate(topic=topic, session_id=session_id)
            async with get_independent_db_session() as db:
                db.add_all(lesson)

                try:
                    await db.commit()
                except SQLAlchemyError as err:
                    await db.rollback()
                    print('SQLAlchemyError' + str(err))
