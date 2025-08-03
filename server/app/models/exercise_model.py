from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.database.database import Base
from app.schemas.exercise_schema import ExerciseDetail

if TYPE_CHECKING:
    from app.models.lesson_model import Lesson


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String)
    constraint: Mapped[str] = mapped_column(String, nullable=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id"), index=True, nullable=True
    )
    case: Mapped[str] = mapped_column(JSON, nullable=True)
    suggest: Mapped[str] = mapped_column(String, nullable=True)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="exercises")

    class Config:
        from_attributes = True

    @staticmethod
    def exercise_from_schema(data: ExerciseDetail):
        exercise = Exercise()

        # Các trường bắt buộc
        exercise.name = data.name
        exercise.description = data.description
        exercise.difficulty = data.difficulty

        # Các trường có thể None
        exercise.constraint = data.constraint or ""
        exercise.suggest = data.suggest or ""

        return exercise
