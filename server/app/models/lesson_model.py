from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.schemas.lesson_schema import Options

if TYPE_CHECKING:
    from app.models.topic_model import Topic
    from app.models.user_model import User
    from app.models.exercise_model import Exercise


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
    )  # Cho câu hỏi quiz
    answer: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # Đáp án đúng cho quiz
    explanation: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Giải thích cho quiz

    # Relationship
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="sections")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(
        String, index=True, unique=True
    )  # ID hiển thị cho người dùng (ví dụ: "1", "2")
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), index=True)
    order: Mapped[int] = mapped_column(Integer)  # Thứ tự bài học trong chủ đề
    next_lesson_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    prev_lesson_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    sections: Mapped[List[LessonSection]] = relationship(
        "LessonSection", back_populates="lesson", cascade="all, delete-orphan"
    )
    topic: Mapped["Topic"] = relationship("Topic", back_populates="lessons")
    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise", back_populates="lesson", cascade="all, delete-orphan"
    )
