from app.schemas.lesson_schema import (
    LessonWithChildSchema,
    LessonSectionResponse,
    ExerciseResponse,
    Options,
)
from sqlalchemy.orm import Session
from typing import Optional

from app.models.lesson_model import Lesson


def model_to_dict(instance):
    return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}


def convert_lesson_to_schema(
    lesson: Lesson, user_id: Optional[int] = None, db: Optional[Session] = None
) -> LessonWithChildSchema:
    """
    Chuyển đổi từ model Lesson sang LessonResponseSchema

    Args:
        lesson: Đối tượng Lesson model

    Returns:
        LessonResponseSchema: Đối tượng schema đã được chuyển đổi
    """
    # Tạo sections data
    sections_data = []
    for section in lesson.sections:
        section_data = {
            "id": section.id,
            "type": section.type,
            "content": section.content,
            "order": section.order,
            "options": None,
            "answer": section.answer,
            "explanation": section.explanation,
        }

        # Xử lý options nếu có
        if section.options and isinstance(section.options, dict):
            if all(key in section.options for key in ["A", "B", "C", "D"]):
                section_data["options"] = Options(
                    A=section.options["A"],
                    B=section.options["B"],
                    C=section.options["C"],
                    D=section.options["D"],
                )

        sections_data.append(LessonSectionResponse(**section_data))

    # Tạo exercises data
    exercises_data = []
    for exercise in lesson.exercises:
        exercises_data.append(
            ExerciseResponse(
                id=exercise.id,
                title=getattr(exercise, "title", None) or getattr(exercise, "name", ""),
                description=exercise.description,
                category=getattr(exercise, "category", None),
                difficulty=exercise.difficulty,
                estimated_time=getattr(exercise, "estimated_time", None),
                completion_rate=getattr(exercise, "completion_rate", None),
                completed=getattr(exercise, "completed", None),
                content=getattr(exercise, "content", None),
                code_template=getattr(exercise, "code_template", None),
                lesson_id=exercise.lesson_id,
            )
        )

    # Kiểm tra trạng thái completed nếu có user_id và db
    is_completed = False
    # Ghi chú: UserLesson model không tồn tại trong codebase hiện tại. Nếu cần,
    # có thể bổ sung sau. Tạm thời đánh dấu False.

    # Tạo lesson response
    return LessonWithChildSchema(
        id=lesson.id,
        external_id=lesson.external_id,
        title=lesson.title,
        description=lesson.description,
        order=lesson.order,
        next_lesson_id=lesson.next_lesson_id,
        prev_lesson_id=lesson.prev_lesson_id,
        sections=sections_data,
        exercises=exercises_data,
        is_completed=is_completed,
    )
