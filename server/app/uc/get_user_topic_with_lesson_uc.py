from typing import List, Iterable

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_async_db
from app.models import Topic, UserLesson
from app.schemas import BaseLesson, UserExcludeSecret
from app.schemas.topic_schema import TopicBase
from app.uc.base_use_case import BaseUseCase
from app.utils.utils import get_current_user


class TopicRepository:
    def __init__(self, db: AsyncSession = Depends(get_async_db)):
        self.db = db

    async def get_topic_by_course_id(self, course_id: int, nested: bool) -> Iterable[Topic]:
        if nested:
            result = await self.db.execute(
                select(Topic).filter(Topic.course_id == course_id).options(selectinload(Topic.lessons), ))
            topics = result.scalars().all()
        else:
            result = await self.db.execute(select(Topic).filter(Topic.course_id == course_id))
            topics = result.scalars().all()

        return topics


class GetUserTopicWithLessonRequest(BaseModel):
    course_id: int


class BaseLessonWithUserStatus(BaseLesson):
    id: int
    is_completed: bool = False


class TopicBaseWithLesson(TopicBase):
    lessons: List[BaseLessonWithUserStatus]
    id: int


class GetUserTopicWithLessonResponseItem(TopicBaseWithLesson):
    pass


class UserLessonRepository:
    def __init__(self, db: AsyncSession = Depends(get_async_db)):
        self.db = db

    async def get_by_user(self, user_id: int) -> Iterable[UserLesson]:
        result = await self.db.execute(select(UserLesson).filter(UserLesson.user_id == user_id))
        user_lessons = result.scalars().all()
        return user_lessons


class GetUserTopicWithLessonUC(BaseUseCase):
    def __init__(self, topic_repository=Depends(TopicRepository), user_lesson_repository=Depends(UserLessonRepository),
                 user: UserExcludeSecret = Depends(get_current_user)):
        self.topic_repository = topic_repository
        self.user_lesson_repository = user_lesson_repository
        self.user = user

    async def execute(self, *args, **kwargs) -> List[GetUserTopicWithLessonResponseItem]:
        data = args[0]
        if not data or not isinstance(data, GetUserTopicWithLessonRequest):
            raise HTTPException(400, "Invalid request data")
        data: GetUserTopicWithLessonRequest
        topics = await self.topic_repository.get_topic_by_course_id(data.course_id, nested=True)
        user_lesson: Iterable[UserLesson] = await self.user_lesson_repository.get_by_user(self.user.id)

        response = [GetUserTopicWithLessonResponseItem.model_validate(topic) for topic in topics]
        for res in response:
            for lesson in res.lessons:
                if any(lesson.id == learned.lesson_id for learned in user_lesson):
                    lesson.is_completed = True

        return response
