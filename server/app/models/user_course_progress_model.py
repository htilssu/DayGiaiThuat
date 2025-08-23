import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class ProgressStatus(str, enum.Enum):
    """Enum for progress status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus),
        nullable=False,
        server_default=ProgressStatus.NOT_STARTED,
        index=True,
    )
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Relationships
    user_course: Mapped["UserCourse"] = relationship(
        "UserCourse", back_populates="progress_records"
    )
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress_records")

    def __repr__(self) -> str:
        return f"<UserCourseProgress(id={self.id}, user_course_id={self.user_course_id}, topic_id={self.topic_id}, lesson_id={self.lesson_id}, status={self.status})>"
