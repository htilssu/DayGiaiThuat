from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.database import Base
from app.models.badge_model import Badge, user_badges
from app.models.learning_progress_model import LearningProgress
from app.models.user_state_model import UserState
from app.models.course_model import Course


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
        learning_paths (List[LearningPath]): Danh sách lộ trình học tập của người dùng (one-to-many)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Các trường thông tin cá nhân
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    bio: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)

    # Relationship với các bảng khác
    # Quan hệ one-to-one với UserState - sử dụng string để tránh circular import
    state: Mapped[UserState] = relationship(
        "UserState", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )

    # Quan hệ one-to-many với LearningProgress - sử dụng string để tránh circular import
    learning_progresses: Mapped[List[LearningProgress]] = relationship(
        "LearningProgress", back_populates="user", cascade="all, delete-orphan"
    )

    # Quan hệ many-to-many với Badge
    badge_collection: Mapped[List[Badge]] = relationship(
        "Badge", secondary=user_badges, back_populates="users"
    )

    # Quan hệ one-to-many với LearningPath
    learning_paths: Mapped[List["LearningPath"]] = relationship(
        "LearningPath", back_populates="user", cascade="all, delete-orphan"
    )

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
        from app.database.database import SessionLocal

        # Lấy danh sách ID khóa học từ learning_progresses
        course_ids = [lp.course_id for lp in self.learning_progresses]

        if not course_ids:
            return []

        # Truy vấn các khóa học từ database
        db = SessionLocal()
        try:
            courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
            return courses
        finally:
            db.close()
