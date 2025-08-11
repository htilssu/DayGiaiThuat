from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class ExerciseTestCase(Base):
    """
    Test case cho bài tập giải thuật

    Thuộc về một `Exercise` qua khóa ngoại `exercise_id`.
    """

    __tablename__ = "exercise_test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), index=True)

    # Nội dung test case
    input_data: Mapped[str] = mapped_column(Text)
    output_data: Mapped[str] = mapped_column(Text)
    explain: Mapped[str] = mapped_column(String, nullable=True)

    # Quan hệ
    exercise: Mapped["Exercise"] = relationship(
        "Exercise", back_populates="test_cases"
    )

    class Config:
        from_attributes = True


if TYPE_CHECKING:
    # For type checkers only to resolve forward references
    from app.models.exercise_model import Exercise
