from typing import TYPE_CHECKING, Optional

from app.database.database import Base
from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.course_model import Course
    from app.models.user_model import User


class UserAssessment(Base):
    """Model lưu trữ kết quả phân tích điểm yếu của người dùng trong từng skill cụ thể"""

    __tablename__ = "user_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Liên kết với user và test session
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    test_session_id: Mapped[str] = mapped_column(
        String, ForeignKey("test_sessions.id"), index=True
    )
    course_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=True, index=True
    )

    # Thông tin skill được đánh giá
    skill_name: Mapped[str] = mapped_column(
        String, nullable=False, comment="Tên skill được đánh giá"
    )

    # Phân tích điểm yếu chi tiết
    weaknesses: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="Các điểm yếu cụ thể trong skill"
    )
    weakness_analysis: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Phân tích chi tiết về các điểm yếu"
    )
    improvement_suggestions: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="Gợi ý cụ thể để cải thiện điểm yếu"
    )

    # Mức độ hiện tại và độ nghiêm trọng
    current_level: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="Mức độ hiện tại của user trong skill"
    )
    weakness_severity: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Mức độ nghiêm trọng của điểm yếu: Low/Medium/High",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="assessments")
    course: Mapped[Optional["Course"]] = relationship(
        "Course", back_populates="user_assessments"
    )
    test_session: Mapped[Optional["TestSession"]] = relationship(
        "TestSession", back_populates="assessment", uselist=False
    )
