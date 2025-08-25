from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.lesson_model import Lesson
    from app.models.user_model import User


class UserLesson(Base):
    __tablename__ = "user_lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lessons.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="user_lessons")
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<UserLesson(id={self.id}, lesson_id={self.lesson_id})>"
