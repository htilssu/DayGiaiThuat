from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.course_model import Course
    from app.models.user_course_progress_model import UserCourseProgress


class UserCourse(Base):
    __tablename__ = "user_courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))
    # Cache fields for quick access to current progress
    current_topic: Mapped[int] = mapped_column(Integer, default=1)
    current_lesson: Mapped[int] = mapped_column(Integer, default=1)
    current_section: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    user: Mapped["User"] = relationship("User")
    course: Mapped["Course"] = relationship("Course")
    progress_records: Mapped[List["UserCourseProgress"]] = relationship(
        "UserCourseProgress", back_populates="user_course", cascade="all, delete-orphan"
    )
