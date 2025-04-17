from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base
from typing import Dict, List, Optional

class UserState(Base):
    """
    Model đại diện cho bảng user_states trong database để lưu trữ trạng thái hiện tại của người dùng
    
    Attributes:
        id (int): ID của trạng thái, là primary key
        user_id (int): ID của người dùng, là foreign key tới bảng users
        last_active (DateTime): Thời điểm hoạt động gần nhất của người dùng
        current_course_id (int): ID của khóa học đang học (nếu có)
        current_lesson_id (int): ID của bài học đang học (nếu có)
        streak_last_date (DateTime): Ngày gần nhất người dùng duy trì streak
        streak_count (int): Số ngày streak hiện tại
        total_points (int): Tổng số điểm tích lũy
        level (int): Cấp độ hiện tại của người dùng
        xp_to_next_level (int): Số điểm kinh nghiệm cần để lên cấp tiếp theo
        daily_goal (int): Mục tiêu học tập hàng ngày (tính bằng phút)
        daily_progress (int): Tiến độ học tập hôm nay (tính bằng phút)
        preferences (JSON): Các tùy chọn cá nhân của người dùng
        notifications (JSON): Cài đặt thông báo của người dùng
        created_at (DateTime): Thời điểm tạo trạng thái
        updated_at (DateTime): Thời điểm cập nhật gần nhất
    """
    __tablename__ = "user_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    current_course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    current_lesson_id = Column(Integer, nullable=True)  # Sẽ thêm foreign key khi tạo bảng Lesson
    streak_last_date = Column(DateTime(timezone=True), nullable=True)
    streak_count = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    xp_to_next_level = Column(Integer, default=100)
    daily_goal = Column(Integer, default=30)  # 30 phút học mỗi ngày
    daily_progress = Column(Integer, default=0)
    
    # Các trường thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Các trường JSON
    preferences = Column(JSON, default=lambda: {
        "theme": "light",
        "notifications_enabled": True,
        "sound_enabled": True,
        "language": "vi"
    })
    
    notifications = Column(JSON, default=lambda: {
        "email": True,
        "push": True,
        "daily_reminder": True,
        "streak_reminder": True,
        "new_content": True
    })
    
    # Relationship với các bảng khác
    user = relationship("User", back_populates="state")
    current_course = relationship("Course") 