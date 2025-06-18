from fastapi import APIRouter, Depends

from app.services.topic_service import TopicService, get_topic_service

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("/topic/{topic_id}")
async def get_tests_by_topic(
    topic_id: str, topic_service: TopicService = Depends(get_topic_service)
):
    return await topic_service.get_topic_by_id(topic_id)
