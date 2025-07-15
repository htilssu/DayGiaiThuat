from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.user_course_progress_model import ProgressStatus


class UserCourseProgressBase(BaseModel):
    """
    Schema cơ bản cho UserCourseProgress

    Attributes:
        user_course_id: ID của user course
        topic_id: ID của topic
        lesson_id: ID của lesson
        status: Trạng thái học tập
    """

    user_course_id: int = Field(..., description="ID của user course")
    topic_id: int = Field(..., description="ID của topic")
    lesson_id: int = Field(..., description="ID của lesson")
    status: ProgressStatus = Field(
        default=ProgressStatus.NOT_STARTED, description="Trạng thái học tập"
    )


class UserCourseProgressCreate(UserCourseProgressBase):
    """
    Schema cho việc tạo progress record mới
    """

    pass


class UserCourseProgressUpdate(BaseModel):
    """
    Schema cho việc cập nhật progress record
    """

    status: Optional[ProgressStatus] = Field(None, description="Trạng thái học tập mới")
    last_viewed_at: Optional[datetime] = Field(
        None, description="Thời điểm xem gần nhất"
    )
    completed_at: Optional[datetime] = Field(None, description="Thời điểm hoàn thành")


class UserCourseProgressResponse(UserCourseProgressBase):
    """
    Schema cho response khi truy vấn progress record

    Attributes:
        id: ID của progress record
        last_viewed_at: Thời điểm xem gần nhất
        completed_at: Thời điểm hoàn thành
        created_at: Thời điểm tạo
        updated_at: Thời điểm cập nhật gần nhất
    """

    id: int = Field(..., description="ID của progress record")
    last_viewed_at: Optional[datetime] = Field(
        None, description="Thời điểm xem gần nhất"
    )
    completed_at: Optional[datetime] = Field(None, description="Thời điểm hoàn thành")
    created_at: datetime = Field(..., description="Thời điểm tạo")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật gần nhất")

    class Config:
        from_attributes = True


class LessonProgressSummary(BaseModel):
    """
    Schema tóm tắt tiến độ học lesson
    """

    topic_id: int = Field(..., description="ID của topic")
    lesson_id: int = Field(..., description="ID của lesson")
    status: ProgressStatus = Field(..., description="Trạng thái học tập")
    completion_percentage: float = Field(..., description="Phần trăm hoàn thành")
    last_viewed_at: Optional[datetime] = Field(
        None, description="Thời điểm xem gần nhất"
    )


class CourseProgressSummary(BaseModel):
    """
    Schema tóm tắt tiến độ học khóa học
    """

    user_course_id: int = Field(..., description="ID của user course")
    total_lessons: int = Field(..., description="Tổng số lesson")
    completed_lessons: int = Field(..., description="Số lesson đã hoàn thành")
    in_progress_lessons: int = Field(..., description="Số lesson đang học")
    not_started_lessons: int = Field(..., description="Số lesson chưa bắt đầu")
    completion_percentage: float = Field(
        ..., description="Phần trăm hoàn thành khóa học"
    )
    current_topic_id: Optional[int] = Field(None, description="ID topic hiện tại")
    current_lesson_id: Optional[int] = Field(None, description="ID lesson hiện tại")
    last_activity_at: Optional[datetime] = Field(None, description="Hoạt động gần nhất")
