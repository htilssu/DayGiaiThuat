from datetime import datetime
from typing import Dict, Optional, TYPE_CHECKING

from app.database.database import Base
from sqlalchemy import ForeignKey, String, Boolean, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.test_model import Test
    from app.models.user_model import User


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"), index=True)

    # Thông tin thời gian
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_activity: Mapped[datetime] = mapped_column(DateTime, index=True)
    time_remaining_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Trạng thái phiên làm bài
    status: Mapped[str] = mapped_column(
        String, default="in_progress"
    )  # in_progress, completed, expired
    is_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    current_question_index: Mapped[int] = mapped_column(Integer, default=0)

    # Lưu trữ câu trả lời hiện tại dưới dạng JSON
    answers: Mapped[Dict] = mapped_column(JSON, default={})

    # Kết quả sau khi nộp bài
    score: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    correct_answers: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    test: Mapped["Test"] = relationship("Test", back_populates="sessions")
    user: Mapped["User"] = relationship("User", back_populates="test_sessions")
