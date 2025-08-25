from typing import List, Optional, TYPE_CHECKING

from app.database.database import Base
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user_state_model import UserState
    from app.models.test_session import TestSession
    from app.models.discussion_model import Discussion
    from app.models.reply_model import Reply
    from app.models.user_assessment_model import UserAssessment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )

    state: Mapped["UserState"] = relationship(back_populates="user")
    test_sessions: Mapped[List["TestSession"]] = relationship(
        "TestSession", back_populates="user"
    )
    discussions: Mapped[List["Discussion"]] = relationship(
        "Discussion", back_populates="user"
    )
    replies: Mapped[List["Reply"]] = relationship("Reply", back_populates="user")
    assessments: Mapped[List["UserAssessment"]] = relationship(
        "UserAssessment", back_populates="user"
    )
