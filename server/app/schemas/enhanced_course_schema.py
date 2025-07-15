"""
Enhanced schemas để thay thế các schema hiện có với nested progress support
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.user_course_progress_model import ProgressStatus
from app.schemas.course_schema import CourseResponse


class LessonWithProgressResponse(BaseModel):
    """
    Schema cho lesson với thông tin progress
    Thay thế cho LessonResponse cũ
    """

    id: int = Field(..., description="ID của lesson")
    external_id: str = Field(..., description="External ID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    description: str = Field(..., description="Mô tả lesson")
    order: int = Field(..., description="Thứ tự lesson trong topic")

    # Progress fields - sẽ được fill từ UserCourseProgress
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


class TopicWithProgressResponse(BaseModel):
    """
    Schema cho topic với lessons và progress nested
    Thay thế cho TopicResponse cũ
    """

    id: int = Field(..., description="ID của topic")
    external_id: Optional[str] = Field(None, description="External ID của topic")
    name: str = Field(..., description="Tên topic")
    description: str = Field(..., description="Mô tả topic")
    order: Optional[int] = Field(None, description="Thứ tự topic trong course")

    # Nested lessons với progress
    lessons: List[LessonWithProgressResponse] = Field(
        default=[], description="Danh sách lessons với progress"
    )

    # Topic-level progress summary
    topic_completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành topic"
    )
    completed_lessons: int = Field(default=0, description="Số lesson đã hoàn thành")
    total_lessons: int = Field(default=0, description="Tổng số lesson trong topic")

    class Config:
        from_attributes = True


class CourseDetailWithProgressResponse(CourseResponse):
    """
    Schema cho course detail với topics, lessons và progress nested
    Thay thế cho CourseDetailResponse cũ
    """

    # Nested topics với progress
    topics: List[TopicWithProgressResponse] = Field(
        default=[], description="Danh sách topics với lessons và progress"
    )

    # Course-level progress summary (chỉ hiển thị khi user đã enroll)
    user_course_id: Optional[int] = Field(
        None, description="ID của user course nếu đã đăng ký"
    )
    overall_completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành tổng thể"
    )
    total_topics: int = Field(default=0, description="Tổng số topic")
    total_lessons: int = Field(default=0, description="Tổng số lesson")
    completed_lessons: int = Field(default=0, description="Số lesson đã hoàn thành")
    in_progress_lessons: int = Field(default=0, description="Số lesson đang học")
    not_started_lessons: int = Field(default=0, description="Số lesson chưa bắt đầu")

    # Current position (chỉ hiển thị khi user đã enroll)
    current_topic_id: Optional[int] = Field(None, description="Topic hiện tại đang học")
    current_lesson_id: Optional[int] = Field(
        None, description="Lesson hiện tại đang học"
    )
    last_activity_at: Optional[datetime] = Field(None, description="Hoạt động gần nhất")

    class Config:
        from_attributes = True


class TopicDetailWithProgressResponse(BaseModel):
    """
    Schema cho topic detail với lessons và progress nested
    Dùng cho endpoint get topic by id
    """

    id: int = Field(..., description="ID của topic")
    external_id: Optional[str] = Field(None, description="External ID của topic")
    name: str = Field(..., description="Tên topic")
    description: str = Field(..., description="Mô tả topic")
    order: Optional[int] = Field(None, description="Thứ tự topic trong course")
    course_id: Optional[int] = Field(None, description="ID của course")

    # Nested lessons với progress
    lessons: List[LessonWithProgressResponse] = Field(
        default=[], description="Danh sách lessons với progress"
    )

    # Topic-level progress summary
    topic_completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành topic"
    )
    completed_lessons: int = Field(default=0, description="Số lesson đã hoàn thành")
    total_lessons: int = Field(default=0, description="Tổng số lesson trong topic")

    # Progress info (chỉ hiển thị khi user đã enroll course)
    user_course_id: Optional[int] = Field(
        None, description="ID của user course nếu đã đăng ký"
    )

    class Config:
        from_attributes = True


class LessonDetailWithProgressResponse(BaseModel):
    """
    Schema cho lesson detail với progress
    Dùng cho endpoint get lesson by id
    """

    id: int = Field(..., description="ID của lesson")
    external_id: str = Field(..., description="External ID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    description: str = Field(..., description="Mô tả lesson")
    order: int = Field(..., description="Thứ tự lesson trong topic")
    topic_id: int = Field(..., description="ID của topic")

    # Lesson content (nếu cần)
    # sections: List[LessonSectionResponse] = Field(...)

    # Progress fields
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

    # Context info (chỉ hiển thị khi user đã enroll course)
    user_course_id: Optional[int] = Field(
        None, description="ID của user course nếu đã đăng ký"
    )

    class Config:
        from_attributes = True
