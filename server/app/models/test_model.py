from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.topic_model import Topic
    from app.models.course_model import Course
    from app.models.test_session import TestSession


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Test có thể thuộc về topic hoặc course
    topic_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("topics.id"), nullable=True
    )
    course_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=True
    )

    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, default=60, nullable=True
    )

    questions: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)

    # Relationships
    topic: Mapped[Optional["Topic"]] = relationship("Topic", back_populates="tests")
    course: Mapped[Optional["Course"]] = relationship("Course", back_populates="tests")
    sessions: Mapped[List["TestSession"]] = relationship(
        "TestSession", back_populates="test"
    )
