from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.topic_model import Topic
from app.schemas.topic_schema import TopicResponse

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/", response_model=List[TopicResponse])
async def get_topics_by_course(
    course_id: int,
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách các chủ đề của một khóa học.
    """
    topics = db.query(Topic).filter(Topic.course_id == course_id).all()
    return topics
