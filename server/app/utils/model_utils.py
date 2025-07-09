from app.models.lesson_model import Lesson
from app.schemas.lesson_schema import (
    LessonResponseSchema,
    LessonSectionSchema,
    ExerciseResponse,
    Options,
)


def model_to_dict(instance):
    return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}


def convert_lesson_to_schema(lesson: Lesson) -> LessonResponseSchema:
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

    # Tạo lesson response
    return LessonResponseSchema(
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
    )
