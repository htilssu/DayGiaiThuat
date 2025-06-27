from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.topic_model import Topic
from app.models.lesson_model import Lesson
from app.schemas.topic_schema import TopicResponse
from app.schemas.lesson_schema import LessonResponse

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


@router.get("/{topic_id}/lessons", response_model=List[LessonResponse])
async def get_lessons_by_topic(
    topic_id: int,
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách bài học của một chủ đề.
    """
    # Kiểm tra topic có tồn tại không
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy topic với ID {topic_id}",
        )

    # Lấy tất cả lessons của topic, sắp xếp theo order
    lessons = (
        db.query(Lesson)
        .filter(Lesson.topic_id == topic_id)
        .order_by(Lesson.order)
        .all()
    )

    return lessons
