from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.lesson_service import LessonService
from app.schemas.lesson_schema import (
    CreateLessonSchema,
    UpdateLessonSchema,
    LessonResponseSchema,
    GenerateLessonRequestSchema,
)

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("/generate", response_model=LessonResponseSchema)
async def generate_lesson(
    request: GenerateLessonRequestSchema,
    topic_id: int,
    order: int,
    db: Session = Depends(get_db),
):
    """
    Generate a lesson using AI with RAG from Pinecone data.
    """
    try:
        lesson_service = LessonService(db)
        lesson = lesson_service.generate_lesson(request, topic_id, order)
        return lesson
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating lesson: {str(e)}",
        )


@router.post("/", response_model=LessonResponseSchema)
async def create_lesson(lesson_data: CreateLessonSchema, db: Session = Depends(get_db)):
    """
    Create a new lesson manually.
    """
    try:
        lesson_service = LessonService(db)
        lesson = lesson_service.create_lesson(lesson_data)
        return lesson
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating lesson: {str(e)}",
        )


@router.get("/{lesson_id}", response_model=LessonResponseSchema)
async def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """
    Get a lesson by ID.
    """
    lesson_service = LessonService(db)
    lesson = lesson_service.get_lesson_by_id(lesson_id)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return lesson


@router.get("/external/{external_id}", response_model=LessonResponseSchema)
async def get_lesson_by_external_id(external_id: str, db: Session = Depends(get_db)):
    """
    Get a lesson by external ID.
    """
    lesson_service = LessonService(db)
    lesson = lesson_service.get_lesson_by_external_id(external_id)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return lesson


@router.get("/topic/{topic_id}", response_model=list[LessonResponseSchema])
async def get_lessons_by_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Get all lessons for a topic.
    """
    lesson_service = LessonService(db)
    lessons = lesson_service.get_lessons_by_topic(topic_id)
    return lessons


@router.put("/{lesson_id}", response_model=LessonResponseSchema)
async def update_lesson(
    lesson_id: int, lesson_data: UpdateLessonSchema, db: Session = Depends(get_db)
):
    """
    Update a lesson.
    """
    lesson_service = LessonService(db)
    lesson = lesson_service.update_lesson(lesson_id, lesson_data)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return lesson


@router.delete("/{lesson_id}")
async def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """
    Delete a lesson.
    """
    lesson_service = LessonService(db)
    success = lesson_service.delete_lesson(lesson_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    return {"message": "Lesson deleted successfully"}
