from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base
from typing import Dict, List, Optional

from app.models.badge import user_badges

class User(Base):
    """
    Model đại diện cho bảng users trong database
    
    Attributes:
        id (int): ID của user, là primary key
        email (str): Email của user, phải là unique
        username (str): Tên đăng nhập của user
        hashed_password (str): Mật khẩu đã được mã hóa
        is_active (bool): Trạng thái hoạt động của tài khoản
        created_at (DateTime): Thời điểm tạo tài khoản
        updated_at (DateTime): Thời điểm cập nhật gần nhất
        full_name (str): Họ và tên đầy đủ của người dùng
        bio (str): Giới thiệu ngắn về bản thân
        avatar_url (str): Đường dẫn đến ảnh đại diện
        stats (Dict): Thống kê người dùng (completed_exercises, completed_courses, total_points, streak_days, level, problems_solved)
        badges (List): Danh sách huy hiệu người dùng
        activities (List): Lịch sử hoạt động của người dùng
        learning_progress (Dict): Tiến độ học tập của người dùng (algorithms, data_structures, dynamic_programming)
        courses (List): Danh sách khóa học đang theo dõi
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Các trường thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Các trường từ ProfileBase
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Các trường JSON để lưu trữ dữ liệu phức tạp
    stats = Column(JSON, default=lambda: {
        "completed_exercises": 0,
        "completed_courses": 0,
        "total_points": 0,
        "streak_days": 0,
        "level": 1,
        "problems_solved": 0
    })
    
    badges = Column(JSON, default=lambda: [
        {
            "id": 1,
            "name": "Người mới",
            "icon": "🔰",
            "description": "Hoàn thành đăng ký tài khoản",
            "unlocked": True
        }
    ])
    
    activities = Column(JSON, default=list)
    
    learning_progress = Column(JSON, default=lambda: {
        "algorithms": 0,
        "data_structures": 0,
        "dynamic_programming": 0
    })
    
    courses = Column(JSON, default=list)
    
    # Relationship với các bảng mới
    state = relationship("UserState", uselist=False, back_populates="user")
    learning_progresses = relationship("LearningProgress", back_populates="user")
    badge_collection = relationship("Badge", secondary=user_badges, back_populates="users") 