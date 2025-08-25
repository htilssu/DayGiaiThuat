from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.lesson_schema import (
    CreateLessonSchema,
    LessonCompleteResponseSchema,
    LessonWithChildSchema,
)
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.lesson_section_service import get_sections_by_lesson
from app.services.lesson_service import LessonService, get_lesson_service
from app.utils.utils import get_current_user, get_current_user_optional

router = APIRouter(prefix="/lessons", tags=["Bài học"])


@router.post("/", response_model=LessonWithChildSchema)
async def create_lesson(
    lesson_data: CreateLessonSchema,
    lesson_service: LessonService = Depends(get_lesson_service),
):
    try:
        lesson = await lesson_service.create_lesson(lesson_data)
        return lesson
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating lesson: {str(e)}",
        )


@router.post("/{lesson_id}/complete", response_model=LessonCompleteResponseSchema)
async def complete_lesson(
    lesson_id: int,
    current_user: UserExcludeSecret = Depends(get_current_user),
    lesson_service: LessonService = Depends(get_lesson_service),
):
    lesson = await lesson_service.complete_lesson(lesson_id, current_user.id)
    return lesson


@router.get("/{lesson_id}/sections")
async def get_lesson_sections(
    lesson_id: int,
):
    sections = get_sections_by_lesson(lesson_id)
    return sections


@router.get("/{lesson_id}", response_model=LessonWithChildSchema)
async def get_lesson(
    lesson_id: int,
    current_user: UserExcludeSecret = Depends(get_current_user_optional),
    lesson_service: LessonService = Depends(get_lesson_service),
):
    lesson = await lesson_service.get_lesson_with_progress(lesson_id, current_user.id)
    return lesson


@router.get("/{lesson_id}/basic", response_model=LessonWithChildSchema)
async def get_lesson_basic_info(
    lesson_id: int, lesson_service: LessonService = Depends(get_lesson_service)
):
    lesson = await lesson_service.get_lesson_by_id(lesson_id)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return lesson


@router.get("/topic/{topic_id}", response_model=list[LessonWithChildSchema])
async def get_lessons_by_topic(
    topic_id: int, lesson_service: LessonService = Depends(get_lesson_service)
):
    lessons = await lesson_service.get_lessons_by_topic(topic_id)
    return lessons
