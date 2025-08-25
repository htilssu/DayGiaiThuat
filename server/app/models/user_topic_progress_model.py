from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base


class UserTopicProgress(Base):
    """
    Model đại diện cho bảng user_topic_progress trong database để lưu trữ tiến độ học tập theo chủ đề
    
    Attributes:
        id (int): ID của tiến độ, là primary key
        user_id (int): ID của người dùng, là foreign key tới bảng users
        topic_id (int): ID của chủ đề, là foreign key tới bảng topics
        progress_percentage (float): Phần trăm hoàn thành chủ đề (0.0 - 100.0)
        lessons_completed (int): Số bài học đã hoàn thành trong chủ đề
        exercises_completed (int): Số bài tập đã hoàn thành trong chủ đề
        last_activity_at (DateTime): Thời điểm hoạt động gần nhất trong chủ đề
        created_at (DateTime): Thời điểm bắt đầu học chủ đề
        updated_at (DateTime): Thời điểm cập nhật gần nhất
    """
    
    __tablename__ = "user_topic_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    progress_percentage: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, server_default="0.0"
    )
    lessons_completed: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    exercises_completed: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="topic_progress")
    topic: Mapped["Topic"] = relationship("Topic", back_populates="user_progress")
    
    def __repr__(self) -> str:
        return f"<UserTopicProgress(id={self.id}, user_id={self.user_id}, topic_id={self.topic_id}, progress={self.progress_percentage}%)>"