from sqlalchemy import Integer, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, List

from app.database.database import Base


class Topic(Base):

    __tablename__ = "topics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(
        String, index=True, unique=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String)
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="topic")
    user_topics: Mapped[List["UserTopic"]] = relationship(
        "UserTopic", back_populates="topic"
    )
    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise", back_populates="topic"
    )
    tests: Mapped[List["Test"]] = relationship("Test", back_populates="topic")
