from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.topic_model import Topic
from app.schemas.topic_schema import (
    CreateTopicSchema,
    UpdateTopicSchema,
    TopicResponse,
    TopicWithLessonsResponse,
)
from app.schemas.lesson_schema import LessonResponseSchema
from app.models.lesson_model import Lesson

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: CreateTopicSchema,
    db: Session = Depends(get_db),
):
    # Check if course exists (optional, for robustness)
    # from app.models.course_model import Course
    # course = db.query(Course).filter(Course.id == topic_data.course_id).first()
    # if not course:
    #     raise HTTPException(status_code=404, detail="Course not found")
    topic = Topic(**topic_data.dict())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/course/{course_id}", response_model=List[TopicResponse])
def list_topics_for_course(course_id: int, db: Session = Depends(get_db)):
    topics = db.query(Topic).filter(Topic.course_id == course_id).order_by(Topic.id).all()
    return topics


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic_by_id(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.get("/{topic_id}/with-lessons", response_model=TopicWithLessonsResponse)
def get_topic_with_lessons(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    lessons = db.query(Lesson).filter(Lesson.topic_id == topic_id).order_by(Lesson.order).all()
    lessons_response = [LessonResponseSchema.model_validate(lesson) for lesson in lessons]
    topic_data = TopicWithLessonsResponse.model_validate(topic)
    topic_data.lessons = lessons_response
    return topic_data


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: UpdateTopicSchema,
    db: Session = Depends(get_db),
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    for key, value in topic_data.dict(exclude_unset=True).items():
        setattr(topic, key, value)
    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    db.delete(topic)
    db.commit()
    return None
