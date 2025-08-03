from sqlalchemy import Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.database import Base
from typing import Optional


class LessonGenerationState(Base):
    __tablename__ = "lesson_generation_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id"), nullable=False
    )
    lesson_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("lessons.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="in_progress"
    )  # e.g., in_progress, completed, failed
    request_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    topic = relationship("Topic")
    lesson = relationship("Lesson")
