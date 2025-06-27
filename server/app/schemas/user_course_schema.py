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


class CourseEnrollmentResponse(BaseModel):
    """
    Schema cho response khi đăng ký khóa học

    Attributes:
        enrollment: Thông tin đăng ký khóa học
        has_entry_test: Có test đầu vào hay không
        entry_test_id: ID của test đầu vào (nếu có)
    """

    enrollment: UserCourseResponse = Field(
        ..., description="Thông tin đăng ký khóa học"
    )
    has_entry_test: bool = Field(..., description="Có test đầu vào hay không")
    entry_test_id: int | None = Field(None, description="ID của test đầu vào (nếu có)")

    class Config:
        """Cấu hình cho Pydantic model"""

        from_attributes = True
