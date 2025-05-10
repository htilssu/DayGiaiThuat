from typing import Dict, List

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Course(Base):
    """
    Model đại diện cho bảng courses trong database
    
    Attributes:
        id (int): ID của khóa học, là primary key
        title (str): Tiêu đề của khóa học
        description (text): Mô tả chi tiết về khóa học
        thumbnail_url (str): Đường dẫn đến ảnh thumbnail của khóa học
        level (str): Cấp độ khó của khóa học (Beginner, Intermediate, Advanced)
        duration (int): Thời lượng ước tính để hoàn thành khóa học (tính bằng phút)
        price (float): Giá của khóa học (0 nếu miễn phí)
        is_published (bool): Trạng thái xuất bản của khóa học
        tags (List): Các thẻ tag liên quan đến khóa học
        sections (List): Các phần học trong khóa học
        requirements (List): Các yêu cầu cần có trước khi học
        what_you_will_learn (List): Những gì người học sẽ đạt được sau khóa học
        learning_path (Dict): Lộ trình học tập theo mô hình Duolingo, bao gồm các đơn vị học tập, bài học và thành tựu
        created_at (DateTime): Thời điểm tạo khóa học
        updated_at (DateTime): Thời điểm cập nhật gần nhất
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    level = Column(String(50), default="Beginner")
    duration = Column(Integer, default=0)  # Thời lượng tính bằng phút
    price = Column(Float, default=0.0)
    is_published = Column(Boolean, default=False)
    
    # Các trường thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Các trường JSON
    tags = Column(String(255), default="")  # Lưu dưới dạng chuỗi các tag cách nhau bởi dấu phẩy
    requirements = Column(Text, nullable=True)  # Lưu dưới dạng JSON string
    what_you_will_learn = Column(Text, nullable=True)  # Lưu dưới dạng JSON string
    learning_path = Column(Text, nullable=True)  # Lưu dưới dạng JSON string lộ trình học tập
    
    # Relationship với các bảng khác
    learning_progresses = relationship("LearningProgress", back_populates="course")
    user_states = relationship("UserState", back_populates="current_course")
    # sections = relationship("CourseSection", back_populates="course")
    # enrollments = relationship("Enrollment", back_populates="course") 