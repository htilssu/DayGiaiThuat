from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base
from typing import Dict, List, Optional

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
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress_percent = Column(Float, default=0.0)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    favorite = Column(Boolean, default=False)
    
    # Các trường thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Các trường JSON
    completed_lessons = Column(JSON, default=list)
    quiz_scores = Column(JSON, default=dict)
    
    # Relationship với các bảng khác
    user = relationship("User", back_populates="learning_progresses")
    course = relationship("Course", back_populates="learning_progresses") 