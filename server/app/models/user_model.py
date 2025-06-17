from typing import TYPE_CHECKING, List, Optional

from app.database.database import Base
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.lesson_model import UserLesson
    from app.models.topic_model import UserTopic


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user_topics: Mapped[List["UserTopic"]] = relationship(
        "UserTopic", back_populates="user"
    )
    user_lessons: Mapped[List["UserLesson"]] = relationship(
        "UserLesson", back_populates="user"
    )
