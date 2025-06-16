from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.topic_model import Topic
    from app.models.user_model import User


class LessonSection(Base):
    __tablename__ = "lesson_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"))
    type: Mapped[str] = mapped_column(
        String, index=True
    )  # "text", "code", "image", "quiz"
    content: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer)
    options: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # Cho câu hỏi quiz
    answer: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
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
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, index=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"))
    order: Mapped[int] = mapped_column(Integer)  # Thứ tự bài học trong chủ đề
    next_lesson_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    prev_lesson_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    sections: Mapped[List[LessonSection]] = relationship(
        "LessonSection", back_populates="lesson", cascade="all, delete-orphan"
    )
    user_lessons: Mapped[List["UserLesson"]] = relationship(
        "UserLesson", back_populates="lesson"
    )
    topic: Mapped["Topic"] = relationship("Topic", back_populates="lessons")


class UserLesson(Base):
    __tablename__ = "user_lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    progress: Mapped[int] = mapped_column(Integer, default=0)  # Tiến độ từ 0-100%
    last_section_index: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Phần cuối cùng đã xem
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )  # Thời gian hoàn thành

    # Relationships
    lesson: Mapped[Lesson] = relationship("Lesson", back_populates="user_lessons")
    user: Mapped["User"] = relationship("User", back_populates="user_lessons")
