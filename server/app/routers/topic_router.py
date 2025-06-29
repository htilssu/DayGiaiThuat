from fastapi import APIRouter, Depends, status
from typing import List

from app.schemas.topic_schema import (
    CreateTopicSchema,
    UpdateTopicSchema,
    TopicResponse,
    TopicWithLessonsResponse,
)
from app.schemas.lesson_schema import LessonResponseSchema
from app.services.topic_service import TopicService, get_topic_service

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: CreateTopicSchema,
    topic_service: TopicService = Depends(get_topic_service),
):
    """Tạo topic mới"""
    topic = await topic_service.create_topic(topic_data)
    return topic


@router.get("/course/{course_id}", response_model=List[TopicResponse])
async def list_topics_for_course(
    course_id: int, topic_service: TopicService = Depends(get_topic_service)
):
    """Lấy danh sách topics theo course ID"""
    topics = await topic_service.get_topics_by_course_id(course_id)
    return topics


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic_by_id(
    topic_id: int, topic_service: TopicService = Depends(get_topic_service)
):
    """Lấy topic theo ID"""
    topic = await topic_service.get_topic_by_id(topic_id)
    return topic


@router.get("/{topic_id}/with-lessons", response_model=TopicWithLessonsResponse)
async def get_topic_with_lessons(
    topic_id: int, topic_service: TopicService = Depends(get_topic_service)
):
    """Lấy topic với lessons"""
    result = await topic_service.get_topic_with_lessons(topic_id)
    topic_data = TopicWithLessonsResponse.model_validate(result["topic"])
    topic_data.lessons = result["lessons"]
    return topic_data


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: UpdateTopicSchema,
    topic_service: TopicService = Depends(get_topic_service),
):
    """Cập nhật topic"""
    topic = await topic_service.update_topic(topic_id, topic_data)
    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int, topic_service: TopicService = Depends(get_topic_service)
):
    """Xóa topic"""
    await topic_service.delete_topic(topic_id)
    return None


@router.get("/", response_model=List[TopicResponse])
async def get_topics_by_course(
    course_id: int,
    topic_service: TopicService = Depends(get_topic_service),
):
    """
    Lấy danh sách các chủ đề của một khóa học.
    """
    topics = await topic_service.get_topics_by_course_id(course_id)
    return topics


@router.get("/{topic_id}/lessons", response_model=List[LessonResponseSchema])
async def get_lessons_by_topic(
    topic_id: int,
    topic_service: TopicService = Depends(get_topic_service),
):
    """
    Lấy danh sách bài học của một chủ đề.
    """
    lessons = await topic_service.get_lessons_by_topic_id(topic_id)
    return lessons
