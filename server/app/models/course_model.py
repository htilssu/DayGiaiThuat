from __future__ import annotations

import enum
from enum import Enum
from typing import List

import sqlalchemy

from app.database.database import Base
from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TestGenerationStatus(str, Enum):
    """Trạng thái tạo bài test"""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    NOT_STARTED = "not_started"


class CourseStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    TOPIC_APPROVED = "TOPIC_APPROVED"
    LESSON_APPROVED = "LESSON_APPROVED"
    EXERCISE_APPROVED = "EXERCISE_APPROVED"
    COMPOSITING = "COMPOSITING"


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
    duration: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(sqlalchemy.Enum(CourseStatus, native_enum = False), nullable=True, default=CourseStatus.COMPOSITING)

    test_generation_status: Mapped[str] = mapped_column(
        String(20), default=TestGenerationStatus.NOT_STARTED
    )

    tags: Mapped[str] = mapped_column(String(255), default="")
    requirements: Mapped[str] = mapped_column(Text, nullable=True)
    what_you_will_learn: Mapped[str] = mapped_column(Text, nullable=True)

    topics: Mapped[List["Topic"]] = relationship(
        "Topic", back_populates="course", cascade="all, delete-orphan"
    )
    user_states: Mapped[List["UserState"]] = relationship(
        back_populates="current_course", cascade="all, delete-orphan"
    )
    tests: Mapped[List["Test"]] = relationship(
        "Test", back_populates="course", cascade="all, delete-orphan"
    )

    user_courses: Mapped[List["UserCourse"]] = relationship(
        "UserCourse", back_populates="course", cascade="all"
    )

    document_processing_jobs: Mapped[List["DocumentProcessingJob"]] = relationship(
        back_populates="course"
    )
    drafts: Mapped[List["CourseDraft"]] = relationship(
        "CourseDraft", back_populates="course", cascade="all, delete-orphan"
    )
    user_assessments: Mapped[List["UserAssessment"]] = relationship(
        "UserAssessment", back_populates="course"
    )
