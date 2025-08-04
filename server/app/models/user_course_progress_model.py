from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.user_course_model import UserCourse


class ProgressStatus(str, enum.Enum):
    """Enum for progress status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserCourseProgress(Base):
    """
    Model để theo dõi tiến độ chi tiết của user trong từng lesson của khóa học

    Attributes:
        id (int): ID của progress record, là primary key
        user_course_id (int): Foreign key đến bảng user_courses
        topic_id (int): ID của topic trong course
        lesson_id (int): ID của lesson trong topic
        status (ProgressStatus): Trạng thái học tập (not_started, in_progress, completed)
        last_viewed_at (datetime): Thời điểm xem lesson gần nhất
        completed_at (datetime): Thời điểm hoàn thành lesson (nullable)
        created_at (datetime): Thời điểm tạo record
        updated_at (datetime): Thời điểm cập nhật gần nhất

    Relationships:
        user_course (UserCourse): Khóa học của user liên quan (many-to-one)
    """

    __tablename__ = "user_course_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    lesson_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus),
        nullable=False,
        default=ProgressStatus.NOT_STARTED,
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

    def __repr__(self) -> str:
        return f"<UserCourseProgress(id={self.id}, user_course_id={self.user_course_id}, topic_id={self.topic_id}, lesson_id={self.lesson_id}, status={self.status})>"
