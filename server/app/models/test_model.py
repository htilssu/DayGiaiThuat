from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.topic_model import Topic
    from app.models.test_session import TestSession


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"))
    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, default=60, nullable=True
    )

    # Lưu trữ cấu trúc câu hỏi dưới dạng JSON
    questions: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="tests")
    sessions: Mapped[List["TestSession"]] = relationship(
        "TestSession", back_populates="test"
    )
