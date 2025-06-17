from fastapi import HTTPException, Depends
from app.models.topic_model import Topic
from app.database.repository import Repository


class TopicService:
    def __init__(
        self,
    ):
        self.repository = Repository[Topic](Topic)

    async def get_topic_by_id(self, topic_id: int) -> Topic:
        topic = await self.repository.get_async(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not exist")
        return topic
