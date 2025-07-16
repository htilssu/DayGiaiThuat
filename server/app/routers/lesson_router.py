from app.schemas.lesson_schema import (
    CreateLessonSchema,
    GenerateLessonRequestSchema,
    LessonCompleteResponseSchema,
    LessonResponseSchema,
    UpdateLessonSchema,
)
from app.schemas.lesson_schema import (
    LessonDetailWithProgressResponse,
)
from app.utils.utils import get_current_user, get_current_user_optional
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.lesson_service import LessonService, get_lesson_service
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/lessons", tags=["Bài học"])


@router.post("/generate", response_model=LessonResponseSchema)
async def generate_lesson(
    request: GenerateLessonRequestSchema,
    topic_id: int,
    order: int,
    lesson_service: LessonService = Depends(get_lesson_service),
):
    """
    Generate a lesson using AI with RAG from Pinecone data.
    """
    try:
        lesson = await lesson_service.generate_lesson(request, topic_id, order)
        return lesson
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating lesson: {str(e)}",
        )


@router.post("/", response_model=LessonResponseSchema)
async def create_lesson(
    lesson_data: CreateLessonSchema,
    lesson_service: LessonService = Depends(get_lesson_service),
):
    """
    Create a new lesson manually.
    """
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
    """
    Complete a lesson.
    """
    lesson = await lesson_service.complete_lesson(lesson_id, current_user.id)
    return lesson


@router.get("/{lesson_id}", response_model=LessonDetailWithProgressResponse)
async def get_lesson(
    lesson_id: int,
    current_user: UserExcludeSecret = Depends(get_current_user_optional),
    lesson_service: LessonService = Depends(get_lesson_service),
):
    """
    Lấy lesson theo ID với progress information

    Returns lesson detail với:
    - Progress status (completed/in_progress/not_started)
    - Last viewed time
    - Completion percentage
    - User course context
    """
    user_id = current_user.id if current_user else None
    lesson = await lesson_service.get_lesson_with_progress(lesson_id, user_id)
    return lesson


@router.get("/{lesson_id}/basic", response_model=LessonResponseSchema)
async def get_lesson_basic_info(
    lesson_id: int, lesson_service: LessonService = Depends(get_lesson_service)
):
    """
    Get basic lesson info without progress (backward compatibility)
    """
    lesson = await lesson_service.get_lesson_by_id(lesson_id)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return lesson


@router.get("/external/{external_id}", response_model=LessonResponseSchema)
async def get_lesson_by_external_id(
    external_id: str, lesson_service: LessonService = Depends(get_lesson_service)
):
    """
    Get a lesson by external ID.
    """
    lesson = await lesson_service.get_lesson_by_external_id(external_id)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return lesson


@router.get("/topic/{topic_id}", response_model=list[LessonResponseSchema])
async def get_lessons_by_topic(
    topic_id: int, lesson_service: LessonService = Depends(get_lesson_service)
):
    """
    Get all lessons for a topic.
    """
    lessons = await lesson_service.get_lessons_by_topic(topic_id)
    return lessons


@router.put("/{lesson_id}", response_model=LessonResponseSchema)
async def update_lesson(
    lesson_id: int,
    lesson_data: UpdateLessonSchema,
    lesson_service: LessonService = Depends(get_lesson_service),
):
    """
    Update a lesson.
    """
    lesson = await lesson_service.update_lesson(lesson_id, lesson_data)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return lesson


@router.delete("/{lesson_id}")
async def delete_lesson(
    lesson_id: int, lesson_service: LessonService = Depends(get_lesson_service)
):
    """
    Delete a lesson.
    """
    success = await lesson_service.delete_lesson(lesson_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return {"message": "Lesson deleted successfully"}
