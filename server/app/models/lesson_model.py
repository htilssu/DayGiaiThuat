from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.user_course_progress_model import ProgressStatus
from app.schemas.lesson_schema import Options

if TYPE_CHECKING:
    pass


class LessonSection(Base):
    __tablename__ = "lesson_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lessons.id"), index=True
    )
    type: Mapped[str] = mapped_column(String)  # "text", "code", "image", "quiz"
    content: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer)
    options: Mapped[Optional[Options]] = mapped_column(
        JSON, nullable=True
    )
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercises.id"), nullable=True)
    answer: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    explanation: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="sections")
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="lesson_section")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), index=True)
    order: Mapped[int] = mapped_column(Integer)

    # Relationships
    sections: Mapped[List[LessonSection]] = relationship(
        "LessonSection", back_populates="lesson", cascade="all, delete-orphan"
    )
    topic: Mapped["Topic"] = relationship("Topic", back_populates="lessons")

    progress_records: Mapped["UserCourseProgress"] = relationship("UserCourseProgress", back_populates="lesson",
                                                                  cascade="all, delete-orphan")

    @property
    def is_completed(self) -> bool:
        if self.progress_records.status == ProgressStatus.COMPLETED.value:
            return True
        else:
            return False
