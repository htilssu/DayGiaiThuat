from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserLessonBase(BaseModel):
    lesson_id: int = Field(..., description="ID của lesson")
    completed_at: Optional[datetime] = Field(None, description="Thời điểm hoàn thành")


class UserLessonCreate(UserLessonBase):
    pass


class UserLessonUpdate(BaseModel):
    last_viewed_at: Optional[datetime] = Field(
        None, description="Thời điểm xem gần nhất"
    )
    completed_at: Optional[datetime] = Field(None, description="Thời điểm hoàn thành")


class UserLessonResponse(UserLessonBase):
    id: int = Field(..., description="ID của progress record")
    last_viewed_at: Optional[datetime] = Field(
        None, description="Thời điểm xem gần nhất"
    )
    created_at: datetime = Field(..., description="Thời điểm tạo")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật gần nhất")

    class Config:
        from_attributes = True


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
