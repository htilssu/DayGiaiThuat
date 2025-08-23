from pydantic import BaseModel

from app.schemas.lesson_schema import (
    LessonWithChildSchema,
    LessonSectionSchema,
    ExerciseResponse,
    Options,
)
from sqlalchemy.orm import Session, DeclarativeBase
from typing import Optional, TypeVar, Type

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


T = TypeVar("T", bound=DeclarativeBase)


def pydantic_to_sqlalchemy_scalar(pydantic_obj: BaseModel, sa_model: Type[T]) -> T:
    try:
        sa_columns = {col.name for col in sa_model.__table__.columns}
        data = pydantic_obj.model_dump()
        filtered_data = {k: v for k, v in data.items() if k in sa_columns}
        return sa_model(**filtered_data)
    except Exception as e:
        print()
        raise ValueError(f"Error converting Pydantic model to SQLAlchemy model: {e}")


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

        sections_data.append(LessonSectionSchema(**section_data))

    # Lấy exercises từ lesson sections
    exercises_data = []
    for section in lesson.sections:
        if section.exercise_id and section.exercise:
            exercise = section.exercise
            exercises_data.append(
                ExerciseResponse(
                    id=exercise.id,
                    title=getattr(exercise, "title", None)
                    or getattr(exercise, "name", ""),
                    description=exercise.description,
                    category=getattr(exercise, "category", None),
                    difficulty=exercise.difficulty,
                    estimated_time=getattr(exercise, "estimated_time", None),
                    completion_rate=getattr(exercise, "completion_rate", None),
                    completed=getattr(exercise, "completed", None),
                    content=getattr(exercise, "content", None),
                    executable=getattr(exercise, "executable", None),
                    code_template=getattr(exercise, "code_template", None),
                    lesson_id=section.lesson_id,
                )
            )

    # Kiểm tra trạng thái completed nếu có user_id và db
    is_completed = False
    # Ghi chú: UserLesson model không tồn tại trong codebase hiện tại. Nếu cần,
    # có thể bổ sung sau. Tạm thời đánh dấu False.

    # Tạo lesson response
    return LessonWithChildSchema(
        id=lesson.id,
        title=lesson.title,
        description=lesson.description,
        topic_id=lesson.topic_id,
        order=lesson.order,
        sections=sections_data,
        exercises=exercises_data,
        is_completed=is_completed,
    )
