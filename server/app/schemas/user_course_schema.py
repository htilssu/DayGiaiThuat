from datetime import datetime
from pydantic import BaseModel, Field


class UserCourseBase(BaseModel):
    """
    Schema cơ bản cho việc đăng ký khóa học

    Attributes:
        user_id: ID của người dùng
        course_id: ID của khóa học
    """

    user_id: int = Field(..., description="ID của người dùng")
    course_id: int = Field(..., description="ID của khóa học")


class UserCourseCreate(UserCourseBase):
    """
    Schema cho việc tạo mới đăng ký khóa học
    """

    pass


class UserCourseResponse(UserCourseBase):
    """
    Schema cho response khi truy vấn thông tin đăng ký khóa học

    Attributes:
        id: ID của đăng ký
        created_at: Thời điểm đăng ký
        updated_at: Thời điểm cập nhật gần nhất
    """

    id: int = Field(..., description="ID của đăng ký")
    created_at: datetime = Field(..., description="Thời điểm đăng ký")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật gần nhất")

    class Config:
        """Cấu hình cho Pydantic model"""

        from_attributes = True
