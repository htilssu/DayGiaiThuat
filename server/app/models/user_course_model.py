from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class UserCourse(Base):
    __tablename__ = "user_courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))

    user: Mapped["User"] = relationship("User")
    course: Mapped["Course"] = relationship("Course")
