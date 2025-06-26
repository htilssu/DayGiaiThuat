from __future__ import annotations
from typing import List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import Boolean, Integer, String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.user_state_model import UserState
    from app.models.topic_model import Topic


class TestGenerationStatus(str, Enum):
    """Trạng thái tạo bài test"""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    NOT_STARTED = "not_started"


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
        test_generation_status (str): Trạng thái tạo bài test đầu vào
        tags (List): Các thẻ tag liên quan đến khóa học
        sections (List): Các phần học trong khóa học
        requirements (List): Các yêu cầu cần có trước khi học
        what_you_will_learn (List): Những gì người học sẽ đạt được sau khóa học
        created_at (DateTime): Thời điểm tạo khóa học
        updated_at (DateTime): Thời điểm cập nhật gần nhất
    """

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(String(500), nullable=True)
    level: Mapped[str] = mapped_column(String(50), default="Beginner")
    duration: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Thời lượng tính bằng phút
    price: Mapped[float] = mapped_column(Float, default=0.0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    # Trạng thái tạo bài test đầu vào
    test_generation_status: Mapped[str] = mapped_column(
        String(20), default=TestGenerationStatus.NOT_STARTED
    )

    # Các trường JSON
    tags: Mapped[str] = mapped_column(
        String(255), default=""
    )  # Lưu dưới dạng chuỗi các tag cách nhau bởi dấu phẩy
    requirements: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # Lưu dưới dạng JSON string
    what_you_will_learn: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # Lưu dưới dạng JSON string
    learning_path: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # Lưu dưới dạng JSON string lộ trình học tập

    user_states: Mapped[List["UserState"]] = relationship(
        back_populates="current_course"
    )
    topics: Mapped[List["Topic"]] = relationship("Topic", back_populates="course")
