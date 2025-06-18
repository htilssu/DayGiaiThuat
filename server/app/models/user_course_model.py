from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class UserCourse(Base):
    __tablename__ = "user_courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    course: Mapped["Course"] = relationship("Course", back_populates="user_courses")
    user: Mapped["User"] = relationship("User", back_populates="user_courses")
