from fastapi import APIRouter, Depends, HTTPException, status
from app.services.lesson_service import LessonService, get_lesson_service
from app.schemas.lesson_schema import (
    LessonWithChildSchema,
    GenerateLessonRequestSchema,
)

router = APIRouter(prefix="/lesson-plans", tags=["Lộ trình học"])


@router.post("/generate-test", response_model=LessonWithChildSchema)
async def generate_lesson_test(
    request: GenerateLessonRequestSchema,
    lesson_service: LessonService = Depends(get_lesson_service),
):
    """
    Generate a lesson for testing purposes with a fixed topic_id and order.
    """
    try:
        lesson = await lesson_service.generate_lesson(request, topic_id=1, order=1)
        return lesson
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating lesson for test: {str(e)}",
        )
