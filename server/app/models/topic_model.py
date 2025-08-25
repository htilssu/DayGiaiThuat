from __future__ import annotations
from sqlalchemy import Integer, String, ARRAY, ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, List, TYPE_CHECKING

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.course_model import Course
    from app.models.lesson_model import Lesson
    from app.models.test_model import Test
    from app.models.skill_model import Skill


class Topic(Base):

    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("course_id", "order", name="uq_course_order"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("courses.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    course: Mapped[Optional["Course"]] = relationship("Course", back_populates="topics")
    lessons: Mapped[List[Lesson]] = relationship(
        "Lesson", back_populates="topic", cascade="all, delete-orphan"
    )
    tests: Mapped[List[Test]] = relationship(
        "Test", back_populates="topic", cascade="all, delete-orphan"
    )
    skills: Mapped[List["Skill"]] = relationship(
        "Skill", back_populates="topic", cascade="all, delete-orphan"
    )
    order: Mapped[int] = mapped_column(Integer, nullable=True)
