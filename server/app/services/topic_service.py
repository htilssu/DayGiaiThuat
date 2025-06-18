from fastapi import Depends, HTTPException
from app.models.topic_model import Topic
from app.database.repository import GetRepository, Repository
from app.database.database import get_db
from sqlalchemy.orm import Session


class TopicService:
    def __init__(
        self,
        repository: Repository[Topic] = Depends(GetRepository(Topic)),
    ):
        self.repository = repository

    async def get_topic_by_id(self, topic_id: int) -> Topic:
        topic = await self.repository.get_async(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not exist")
        return topic


def get_topic_service(db: Session = Depends(get_db)):
    repository = Repository(Topic, db)
    return TopicService(repository)
