from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.schemas.exercise_schema import ExerciseDetail

if TYPE_CHECKING:
    from app.models.lesson_model import LessonSection
    from app.models.exercise_test_case_model import ExerciseTestCase


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    difficulty: Mapped[str] = mapped_column(String)
    estimated_time: Mapped[str | None] = mapped_column(String, nullable=True)
    completion_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    executable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    code_template: Mapped[str | None] = mapped_column(Text, nullable=True)

    lesson_section: Mapped["LessonSection"] = relationship(
        "LessonSection", back_populates="exercise"
    )
    test_cases: Mapped[list["ExerciseTestCase"]] = relationship(
        "ExerciseTestCase",
        back_populates="exercise",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    class Config:
        from_attributes = True

    @staticmethod
    def exercise_from_schema(data: ExerciseDetail):
        exercise = Exercise()

        exercise.title = (
            getattr(data, "title", None) or getattr(data, "name", None) or ""
        )
        exercise.description = data.description
        exercise.difficulty = data.difficulty

        exercise.category = getattr(data, "category", None)
        exercise.estimated_time = getattr(data, "estimated_time", None)
        exercise.completion_rate = getattr(data, "completion_rate", None)
        exercise.completed = getattr(data, "completed", None)
        exercise.content = getattr(data, "content", None)
        exercise.executable = getattr(data, "executable", None)
        exercise.code_template = getattr(data, "code_template", None)

        return exercise
