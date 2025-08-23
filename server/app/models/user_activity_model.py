import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base


class ActivityType(str, enum.Enum):
    """Enum for activity types"""
    
    EXERCISE = "exercise"
    COURSE = "course" 
    DISCUSSION = "discussion"
    LESSON = "lesson"
    TEST = "test"
    BADGE = "badge"


class UserActivity(Base):
    """
    Model đại diện cho bảng user_activities trong database để lưu trữ hoạt động của người dùng
    
    Attributes:
        id (int): ID của hoạt động, là primary key
        user_id (int): ID của người dùng, là foreign key tới bảng users
        activity_type (ActivityType): Loại hoạt động (exercise, course, discussion, lesson, test, badge)
        activity_name (str): Tên hoạt động
        description (str): Mô tả chi tiết hoạt động
        score (int): Điểm số đạt được (nếu có)
        progress (str): Tiến độ hoàn thành (nếu có)
        related_id (int): ID của đối tượng liên quan (exercise_id, course_id, etc.)
        created_at (DateTime): Thời điểm tạo hoạt động
    """
    
    __tablename__ = "user_activities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType), nullable=False, index=True
    )
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    progress: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="activities")
    
    def __repr__(self) -> str:
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type={self.activity_type}, name='{self.activity_name}')>"