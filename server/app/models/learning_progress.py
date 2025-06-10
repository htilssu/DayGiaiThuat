from datetime import datetime
from sqlalchemy import Boolean, Integer, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class LearningProgress(Base):
    """
    Model đại diện cho bảng learning_progress trong database để theo dõi tiến độ học tập của người dùng

    Attributes:
        id (int): ID của tiến độ học tập, là primary key
        user_id (int): ID của người dùng, là foreign key tới bảng users
        course_id (int): ID của khóa học, là foreign key tới bảng courses
        progress_percent (float): Phần trăm hoàn thành của khóa học (0-100)
        last_accessed (DateTime): Thời điểm truy cập gần nhất vào khóa học
        is_completed (bool): Trạng thái hoàn thành của khóa học
        completion_date (DateTime): Thời điểm hoàn thành khóa học (nếu đã hoàn thành)
        notes (Text): Ghi chú của người dùng về khóa học
        favorite (bool): Đánh dấu khóa học yêu thích
        completed_lessons (JSON): Danh sách các bài học đã hoàn thành
        quiz_scores (JSON): Điểm số các bài kiểm tra trong khóa học
        created_at (DateTime): Thời điểm bắt đầu học khóa học
        updated_at (DateTime): Thời điểm cập nhật tiến độ gần nhất
    """

    __tablename__ = "learning_progresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=False
    )
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    last_accessed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    # Các trường JSON
    completed_lessons: Mapped[list] = mapped_column(JSON, default=list)
    quiz_scores: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationship với các bảng khác
    user: Mapped["User"] = relationship(back_populates="learning_progresses")
    course: Mapped["Course"] = relationship(back_populates="learning_progresses")
