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
        first_name (str): Tên của người dùng
        last_name (str): Họ của người dùng
        bio (str): Giới thiệu ngắn về bản thân
        avatar_url (str): Đường dẫn đến ảnh đại diện
        
    Relationships:
        state (UserState): Thông tin trạng thái người dùng (one-to-one)
        learning_progresses (List[LearningProgress]): Danh sách tiến độ học tập (one-to-many)
        badge_collection (List[Badge]): Danh sách huy hiệu (many-to-many)
        enrolled_courses (List[Course]): Danh sách khóa học đã đăng ký (thông qua learning_progresses)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Các trường thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Các trường thông tin cá nhân
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Relationship với các bảng khác
    # Quan hệ one-to-one với UserState
    state = relationship("UserState", uselist=False, back_populates="user", cascade="all, delete-orphan")
    
    # Quan hệ one-to-many với LearningProgress
    learning_progresses = relationship("LearningProgress", back_populates="user", cascade="all, delete-orphan")
    
    # Quan hệ many-to-many với Badge
    badge_collection = relationship("Badge", secondary=user_badges, back_populates="users")
    
    @property
    def full_name(self):
        """
        Trả về họ và tên đầy đủ của người dùng
        
        Returns:
            str: Họ và tên đầy đủ
        """
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return None
    
    @property
    def enrolled_courses(self):
        """
        Lấy danh sách các khóa học đã đăng ký thông qua learning_progresses
        
        Returns:
            List: Danh sách các Course
        """
        from sqlalchemy.orm import Session
        from app.database.database import SessionLocal
        
        # Lấy danh sách ID khóa học từ learning_progresses
        course_ids = [lp.course_id for lp in self.learning_progresses]
        
        if not course_ids:
            return []
            
        # Truy vấn các khóa học từ database
        db = SessionLocal()
        try:
            from app.models.course import Course
            courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
            return courses
        finally:
            db.close() 