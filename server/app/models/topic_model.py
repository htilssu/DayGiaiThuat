from __future__ import annotations
from sqlalchemy import Integer, String, ARRAY, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, List, TYPE_CHECKING

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.course_model import Course
    from app.models.lesson_model import Lesson
    from app.models.user_topic_model import UserTopic
    from app.models.test_model import Test


class Topic(Base):

    __tablename__ = "topics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("courses.id"), nullable=True
    )
    external_id: Mapped[str] = mapped_column(
        String, index=True, unique=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String)
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    course: Mapped[Optional["Course"]] = relationship("Course", back_populates="topics")
    lessons: Mapped[List[Lesson]] = relationship("Lesson", back_populates="topic")
    user_topics: Mapped[List[UserTopic]] = relationship(
        "UserTopic", back_populates="topic"
    )
    tests: Mapped[List[Test]] = relationship("Test", back_populates="topic")
    order: Mapped[int] = mapped_column(Integer, nullable=True)
