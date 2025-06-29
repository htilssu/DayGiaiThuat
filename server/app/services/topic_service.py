from typing import Any, Dict, List

from app.database.database import get_db
from app.models.topic_model import Topic
from app.models.lesson_model import Lesson
from app.models.user_topic_model import UserTopic
from app.schemas.topic_schema import CreateTopicSchema, UpdateTopicSchema
from app.schemas.lesson_schema import LessonResponseSchema
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session


class TopicService:
    def __init__(
        self,
        db: Session = Depends(get_db),
    ):
        self.db = db

    async def create_topic(self, topic_data: CreateTopicSchema) -> Topic:
        """Tạo topic mới"""
        topic = Topic(**topic_data.dict())
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    async def get_topic_by_id(self, topic_id: int) -> Topic:
        """Lấy topic theo ID"""
        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        return topic

    async def get_topics_by_course_id(self, course_id: int) -> List[Topic]:
        """Lấy danh sách topics theo course ID"""
        topics = (
            self.db.query(Topic)
            .filter(Topic.course_id == course_id)
            .order_by(Topic.id)
            .all()
        )
        return topics

    async def get_topic_with_lessons(self, topic_id: int) -> Dict[str, Any]:
        """Lấy topic với lessons"""
        topic = await self.get_topic_by_id(topic_id)
        lessons = (
            self.db.query(Lesson)
            .filter(Lesson.topic_id == topic_id)
            .order_by(Lesson.order)
            .all()
        )
        lessons_response = [
            LessonResponseSchema.model_validate(lesson) for lesson in lessons
        ]
        return {"topic": topic, "lessons": lessons_response}

    async def get_lessons_by_topic_id(self, topic_id: int) -> List[Lesson]:
        """Lấy danh sách lessons theo topic ID"""
        # Kiểm tra topic có tồn tại không
        await self.get_topic_by_id(topic_id)

        # Lấy tất cả lessons của topic, sắp xếp theo order
        lessons = (
            self.db.query(Lesson)
            .filter(Lesson.topic_id == topic_id)
            .order_by(Lesson.order)
            .all()
        )
        return lessons

    async def update_topic(self, topic_id: int, topic_data: UpdateTopicSchema) -> Topic:
        """Cập nhật topic"""
        topic = await self.get_topic_by_id(topic_id)
        for key, value in topic_data.dict(exclude_unset=True).items():
            setattr(topic, key, value)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    async def delete_topic(self, topic_id: int) -> None:
        """Xóa topic"""
        topic = await self.get_topic_by_id(topic_id)
        self.db.delete(topic)
        self.db.commit()

    def get_user_topics_by_course_id(
        self, course_id: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """Lấy topics với trạng thái user"""
        topics_with_user_state = (
            self.db.query(Topic, UserTopic)
            .join(UserTopic, Topic.id == UserTopic.topic_id, isouter=True)
            .filter(Topic.course_id == course_id, UserTopic.user_id == user_id)
            .all()
        )

        user_topics = []
        for topic, user_topic in topics_with_user_state:
            topic_data = topic.__dict__
            topic_data["user_topic_state"] = user_topic.__dict__ if user_topic else None
            user_topics.append(topic_data)

        return user_topics


def get_topic_service(db: Session = Depends(get_db)):
    return TopicService(db)
