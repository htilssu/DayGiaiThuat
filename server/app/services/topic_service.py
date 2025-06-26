from typing import Any, Dict, List, Optional

from app.database.database import get_db
from app.models.topic_model import Topic
from app.models.user_topic_model import UserTopic
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session


class TopicService:
    def __init__(
        self,
        db: Session = Depends(get_db),
    ):
        self.db = db

    async def get_topic_by_id(self, topic_id: int) -> Topic:
        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not exist")
        return topic

    def get_user_topics_by_course_id(
        self, course_id: str, user_id: str
    ) -> List[Dict[str, Any]]:
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
