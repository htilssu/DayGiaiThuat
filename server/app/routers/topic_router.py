from fastapi import APIRouter, Depends, status
from typing import List

from app.schemas.topic_schema import (
    CreateTopicSchema,
    TopicDetailWithProgressResponse,
    UpdateTopicSchema,
    TopicWithLesson,
)

from app.schemas.lesson_schema import LessonWithChildSchema
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.topic_service import TopicService, get_topic_service
from app.utils.utils import get_current_user_optional

router = APIRouter(prefix="/topics", tags=["Chủ đề"])


@router.post("/", response_model=TopicWithLesson, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: CreateTopicSchema,
    topic_service: TopicService = Depends(get_topic_service),
):
    """Tạo topic mới"""
    topic = await topic_service.create_topic(topic_data)
    return topic


@router.get("/course/{course_id}", response_model=List[TopicWithLesson])
async def list_topics_for_course(
    course_id: int, topic_service: TopicService = Depends(get_topic_service)
):
    """Lấy danh sách topics theo course ID"""
    topics = await topic_service.get_topics_by_course_id(course_id)
    return topics


@router.get("/{topic_id}", response_model=TopicDetailWithProgressResponse)
async def get_topic_by_id(
    topic_id: int,
    current_user: UserExcludeSecret = Depends(get_current_user_optional),
    topic_service: TopicService = Depends(get_topic_service),
):
    """
    Lấy topic theo ID với lessons và progress nested

    Returns topic detail với:
    - Danh sách lessons với progress status
    - Topic completion percentage
    - Progress summary
    """
    user_id = current_user.id if current_user else None
    topic = await topic_service.get_topic_with_progress(topic_id, user_id)
    return topic


@router.get("/{topic_id}/basic", response_model=TopicWithLesson)
async def get_topic_basic_info(
    topic_id: int, topic_service: TopicService = Depends(get_topic_service)
):
    """Lấy basic topic info không có progress (backward compatibility)"""
    topic = await topic_service.get_topic_by_id(topic_id)
    return topic


@router.get("/{topic_id}/with-lessons", response_model=TopicWithLesson)
async def get_topic_with_lessons(
    topic_id: int, topic_service: TopicService = Depends(get_topic_service)
):
    """Lấy topic"""
    result = await topic_service.get_topic_by_id(topic_id)

    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Topic not found")

    return result


@router.put("/{topic_id}", response_model=TopicWithLesson)
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


@router.get("/", response_model=List[TopicWithLesson])
async def get_topics_by_course(
    course_id: int,
    topic_service: TopicService = Depends(get_topic_service),
):
    """
    Lấy danh sách các chủ đề của một khóa học.
    """
    topics = await topic_service.get_topics_by_course_id(course_id)
    return topics


@router.get("/{topic_id}/lessons", response_model=List[LessonWithChildSchema])
async def get_lessons_by_topic(
    topic_id: int,
    topic_service: TopicService = Depends(get_topic_service),
):
    """
    Lấy danh sách bài học của một chủ đề.
    """
    lessons = await topic_service.get_lessons_by_topic_id(topic_id)
    return lessons
