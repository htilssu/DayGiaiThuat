from datetime import datetime
from typing import Dict, Optional, TYPE_CHECKING
import uuid

from app.database.database import Base
from sqlalchemy import ForeignKey, String, Boolean, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.test_model import Test
    from app.models.user_model import User
    from app.models.user_assessment_model import UserAssessment


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"), index=True)

    # Thông tin thời gian
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, index=True
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, index=True, default=lambda: datetime.now()
    )
    time_remaining_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Trạng thái phiên làm bài
    status: Mapped[str] = mapped_column(
        String, default="pending"
    )  # pending, in_progress, completed, expired
    is_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    current_question_index: Mapped[int] = mapped_column(Integer, default=0)

    # Lưu trữ câu trả lời hiện tại dưới dạng JSON
    answers: Mapped[Dict] = mapped_column(JSON, default=lambda: {})

    # Kết quả sau khi nộp bài
    score: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    correct_answers: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Thời gian tạo và cập nhật (đồng bộ với database schema)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), index=True
    )

    # Relationships
    test: Mapped["Test"] = relationship("Test", back_populates="sessions")
    user: Mapped["User"] = relationship("User", back_populates="test_sessions")
    assessment: Mapped[Optional["UserAssessment"]] = relationship(
        "UserAssessment", back_populates="test_session", uselist=False
    )
