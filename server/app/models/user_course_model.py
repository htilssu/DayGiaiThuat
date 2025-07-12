from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class UserCourse(Base):
    __tablename__ = "user_courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))
    current_topic: Mapped[int] = mapped_column(Integer, default=1)
    current_lesson: Mapped[int] = mapped_column(Integer, default=1)
    current_section: Mapped[int] = mapped_column(Integer, default=1)

    user: Mapped["User"] = relationship("User")
    course: Mapped["Course"] = relationship("Course")
