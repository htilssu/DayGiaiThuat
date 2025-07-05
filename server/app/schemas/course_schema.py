from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field
from app.models.course_model import TestGenerationStatus

if TYPE_CHECKING:
    from app.schemas.topic_schema import TopicWithLessonsResponse


class TopicBase(BaseModel):
    """
    Schema cơ bản cho chủ đề

    Attributes:
        name: Tên chủ đề
        description: Mô tả chi tiết về chủ đề
        prerequisites: Danh sách các điều kiện tiên quyết
    """

    name: str = Field(..., min_length=1, max_length=255, description="Tên chủ đề")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về chủ đề")
    prerequisites: Optional[List[str]] = Field(
        None, description="Danh sách các điều kiện tiên quyết"
    )


class TopicResponse(TopicBase):
    """
    Schema cho response khi truy vấn thông tin chủ đề

    Attributes:
        id: ID của chủ đề
        external_id: ID hiển thị cho người dùng
        course_id: ID của khóa học chứa chủ đề này
    """

    id: int = Field(..., description="ID của chủ đề")
    external_id: Optional[str] = Field(None, description="ID hiển thị cho người dùng")
    course_id: int = Field(..., description="ID của khóa học chứa chủ đề này")

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    """
    Schema cơ bản cho khóa học

    Attributes:
        title: Tiêu đề của khóa học
        description: Mô tả chi tiết về khóa học
        thumbnail_url: Đường dẫn đến ảnh thumbnail của khóa học
        level: Cấp độ khó của khóa học (Beginner, Intermediate, Advanced)
        duration: Thời lượng ước tính để hoàn thành khóa học (tính bằng phút)
        price: Giá của khóa học (0 nếu miễn phí)
        is_published: Trạng thái xuất bản của khóa học
        tags: Các thẻ tag liên quan đến khóa học
        requirements: Các yêu cầu cần có trước khi học (JSON string)
        what_you_will_learn: Những gì người học sẽ đạt được sau khóa học (JSON string)
    """

    title: str = Field(
        ..., min_length=3, max_length=255, description="Tiêu đề của khóa học"
    )
    description: Optional[str] = Field(None, description="Mô tả chi tiết về khóa học")
    thumbnail_url: Optional[str] = Field(
        None, max_length=500, description="Đường dẫn đến ảnh thumbnail của khóa học"
    )
    level: Optional[str] = Field("Beginner", description="Cấp độ khó của khóa học")
    duration: Optional[int] = Field(
        0,
        ge=0,
        description="Thời lượng ước tính để hoàn thành khóa học (tính bằng phút)",
    )
    price: Optional[float] = Field(
        0.0, ge=0, description="Giá của khóa học (0 nếu miễn phí)"
    )
    is_published: Optional[bool] = Field(
        False, description="Trạng thái xuất bản của khóa học"
    )
    tags: Optional[str] = Field("", description="Các thẻ tag liên quan đến khóa học")
    requirements: Optional[str] = Field(
        None, description="Các yêu cầu cần có trước khi học (JSON string)"
    )
    what_you_will_learn: Optional[str] = Field(
        None, description="Những gì người học sẽ đạt được sau khóa học (JSON string)"
    )


class CourseCreate(CourseBase):
    """
    Schema cho việc tạo mới khóa học
    """

    pass


class CourseUpdate(BaseModel):
    """
    Schema cho việc cập nhật khóa học

    Note:
        Các trường đều là Optional vì khi cập nhật không nhất thiết phải cung cấp tất cả các trường.
    """

    title: Optional[str] = Field(
        None, min_length=3, max_length=255, description="Tiêu đề của khóa học"
    )
    description: Optional[str] = Field(None, description="Mô tả chi tiết về khóa học")
    thumbnail_url: Optional[str] = Field(
        None, max_length=500, description="Đường dẫn đến ảnh thumbnail của khóa học"
    )
    level: Optional[str] = Field(None, description="Cấp độ khó của khóa học")
    duration: Optional[int] = Field(
        None,
        ge=0,
        description="Thời lượng ước tính để hoàn thành khóa học (tính bằng phút)",
    )
    price: Optional[float] = Field(
        None, ge=0, description="Giá của khóa học (0 nếu miễn phí)"
    )
    is_published: Optional[bool] = Field(
        None, description="Trạng thái xuất bản của khóa học"
    )
    tags: Optional[str] = Field(None, description="Các thẻ tag liên quan đến khóa học")
    requirements: Optional[str] = Field(
        None, description="Các yêu cầu cần có trước khi học (JSON string)"
    )
    what_you_will_learn: Optional[str] = Field(
        None, description="Những gì người học sẽ đạt được sau khóa học (JSON string)"
    )


class CourseResponse(CourseBase):
    """
    Schema cho response khi truy vấn thông tin khóa học

    Attributes:
        id: ID của khóa học
        created_at: Thời điểm tạo khóa học
        updated_at: Thời điểm cập nhật gần nhất
        topics: Danh sách các chủ đề trong khóa học
        test_generation_status: Trạng thái tạo bài test đầu vào
        is_enrolled: Trạng thái đăng ký của người dùng hiện tại (chỉ có khi người dùng đã đăng nhập)
    """

    id: int = Field(..., description="ID của khóa học")
    created_at: datetime = Field(..., description="Thời điểm tạo khóa học")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật gần nhất")
    topics: Optional[List[TopicResponse]] = Field(
        None, description="Danh sách các chủ đề trong khóa học"
    )
    test_generation_status: str = Field(
        TestGenerationStatus.NOT_STARTED, description="Trạng thái tạo bài test đầu vào"
    )
    is_enrolled: Optional[bool] = Field(
        False, description="Trạng thái đăng ký của người dùng hiện tại"
    )

    class Config:
        """Cấu hình cho Pydantic model"""

        from_attributes = True


class CourseDetailResponse(CourseResponse):
    """
    Schema cho response chi tiết khóa học bao gồm cả topics và lessons
    """

    topics: List["TopicWithLessonsResponse"] = Field(
        default_factory=list, description="Danh sách topics và lessons"
    )

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    """
    Schema cho response khi lấy danh sách khóa học với phân trang

    Attributes:
        items: Danh sách các khóa học
        total: Tổng số khóa học
        page: Số trang hiện tại
        limit: Số lượng item mỗi trang
        totalPages: Tổng số trang
    """

    items: List[CourseResponse]
    total: int
    page: int
    limit: int
    totalPages: int


# Rebuild model after TopicWithLessonsResponse is available
def rebuild_course_models():
    """Rebuild course models để resolve forward references"""
    try:
        CourseDetailResponse.model_rebuild()
    except Exception:
        pass
