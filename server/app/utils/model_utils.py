from app.schemas.lesson_schema import (
    LessonWithChildSchema,
    LessonSectionSchema,
    ExerciseResponse,
    Options,
)
from sqlalchemy.orm import Session
from typing import Optional

from app.models.lesson_model import Lesson


def model_to_dict(instance, deep=False):
    data = {}
    for c in instance.__table__.columns:
        data[c.name] = getattr(instance, c.name)

    if deep:
        for rel in instance.__mapper__.relationships:
            value = getattr(instance, rel.key)
            if value is None:
                data[rel.key] = None
            elif isinstance(value, list):
                data[rel.key] = [model_to_dict(i, deep=False) for i in value]
            else:
                data[rel.key] = model_to_dict(value, deep=False)

    return data


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

        sections_data.append(LessonSectionSchema(**section_data))

    # Tạo exercises data
    exercises_data = []
    for exercise in lesson.exercises:
        exercises_data.append(
            ExerciseResponse(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                difficulty=exercise.difficulty,
                constraint=exercise.constraint,
                suggest=exercise.suggest,
                lesson_id=exercise.lesson_id,
            )
        )

    # Kiểm tra trạng thái completed nếu có user_id và db
    is_completed = False
    if user_id and db:
        user_lesson = (
            db.query(UserLesson)
            .filter(UserLesson.user_id == user_id, UserLesson.lesson_id == lesson.id)
            .first()
        )
        if user_lesson:
            is_completed = user_lesson.is_completed

    # Tạo lesson response
    return LessonWithChildSchema(
        id=lesson.id,
        external_id=lesson.external_id,
        title=lesson.title,
        description=lesson.description,
        topic_id=lesson.topic_id,
        order=lesson.order,
        next_lesson_id=lesson.next_lesson_id,
        prev_lesson_id=lesson.prev_lesson_id,
        sections=sections_data,
        exercises=exercises_data,
        is_completed=is_completed,
    )
