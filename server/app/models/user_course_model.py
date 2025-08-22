import enum
from typing import List

from sqlalchemy import Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class UserCourseStatus(str, enum.Enum):
    PASSED = "passed"
    LEARNING = "learning"
    COMPLETED = "completed"


class UserCourse(Base):
    __tablename__ = "user_courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))
    current_topic: Mapped[int] = mapped_column(Integer, default=1)
    current_lesson: Mapped[int] = mapped_column(Integer, default=1)
    current_section: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        default=UserCourseStatus.LEARNING.value,
        index=True,
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    course: Mapped["Course"] = relationship("Course")
    progress_records: Mapped[List["UserCourseProgress"]] = relationship(
        "UserCourseProgress", back_populates="user_course", cascade="all, delete-orphan"
    )
