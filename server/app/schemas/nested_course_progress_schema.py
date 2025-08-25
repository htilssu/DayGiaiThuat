"""
Schema cho response dạng nested với ORM + Response Schema
Triển khai cách 2: Query tất cả topics với lessons nested,
sau đó gắn progress status cho từng lesson
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.user_course_progress_model import ProgressStatus
from app.schemas.topic_schema import TopicBase


class LessonWithProgressSchema(BaseModel):
    """
    Schema cho lesson với thông tin progress
    """

    id: int = Field(..., description="ID của lesson")
    external_id: str = Field(..., description="External ID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    description: str = Field(..., description="Mô tả lesson")
    order: int = Field(..., description="Thứ tự lesson trong topic")
    status: ProgressStatus = Field(
        default=ProgressStatus.NOT_STARTED, description="Trạng thái học tập"
    )
    last_viewed_at: Optional[datetime] = Field(
        None, description="Thời điểm xem gần nhất"
    )
    completed_at: Optional[datetime] = Field(None, description="Thời điểm hoàn thành")
    completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành"
    )

    class Config:
        from_attributes = True


class TopicWithProgressSchema(TopicBase):
    """
    Schema cho topic với danh sách lessons và progress
    """

    id: int = Field(..., description="ID của topic")
    external_id: Optional[str] = Field(None, description="External ID của topic")
    order: Optional[int] = Field(None, description="Thứ tự topic trong course")
    lessons: List[LessonWithProgressSchema] = Field(
        default=[], description="Danh sách lessons với progress"
    )
    topic_completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành topic"
    )
    completed_lessons: int = Field(default=0, description="Số lesson đã hoàn thành")
    total_lessons: int = Field(default=0, description="Tổng số lesson trong topic")

    class Config:
        from_attributes = True


class CourseWithNestedProgressSchema(BaseModel):
    """
    Schema cho course với topics và lessons nested, bao gồm progress
    """

    user_course_id: int = Field(..., description="ID của user course")
    course_id: int = Field(..., description="ID của course")
    course_title: str = Field(..., description="Tiêu đề khóa học")
    course_description: Optional[str] = Field(None, description="Mô tả khóa học")
    topics: List[TopicWithProgressSchema] = Field(
        default=[], description="Danh sách topics với lessons và progress"
    )

    # Thống kê tổng thể
    total_topics: int = Field(default=0, description="Tổng số topic")
    total_lessons: int = Field(default=0, description="Tổng số lesson")
    completed_lessons: int = Field(default=0, description="Số lesson đã hoàn thành")
    in_progress_lessons: int = Field(default=0, description="Số lesson đang học")
    not_started_lessons: int = Field(default=0, description="Số lesson chưa bắt đầu")
    overall_completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành tổng thể"
    )

    # Thông tin hiện tại
    current_topic_id: Optional[int] = Field(None, description="Topic hiện tại đang học")
    current_lesson_id: Optional[int] = Field(
        None, description="Lesson hiện tại đang học"
    )
    last_activity_at: Optional[datetime] = Field(None, description="Hoạt động gần nhất")

    class Config:
        from_attributes = True


class ProgressMapResponse(BaseModel):
    """
    Schema cho progress map - mapping lesson_id -> status
    Dùng để optimize performance khi cần query nhanh
    """

    user_course_id: int = Field(..., description="ID của user course")
    progress_map: dict[int, dict] = Field(
        default={},
        description="Map lesson_id -> {status, last_viewed_at, completed_at}",
    )
    summary: dict = Field(default={}, description="Thống kê tóm tắt")

    class Config:
        from_attributes = True


class LessonProgressMap(BaseModel):
    """
    Schema chi tiết cho từng item trong progress map
    """

    status: ProgressStatus = Field(..., description="Trạng thái lesson")
    last_viewed_at: Optional[datetime] = Field(
        None, description="Thời điểm xem gần nhất"
    )
    completed_at: Optional[datetime] = Field(None, description="Thời điểm hoàn thành")
    completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành"
    )

    class Config:
        from_attributes = True
