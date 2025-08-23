from datetime import datetime
from typing import List, Optional

from app.models.course_model import TestGenerationStatus
from app.schemas.topic_schema import TopicWithLesson, TopicWithProgressResponse
from pydantic import BaseModel, Field


class CourseBase(BaseModel):


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

    class Config:
        from_attributes = True

class CourseBaseUser(CourseBase):
    status : Optional[str] = None


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

    @classmethod
    def from_model(cls, model):
        data = {}
        for field_name in cls.model_fields.keys():
            value = getattr(model, field_name, None)
            data[field_name] = value
        return cls(**data)


class CourseResponse(CourseBase):
    id: int = Field(..., description="ID của khóa học")
    created_at: datetime = Field(..., description="Thời điểm tạo khóa học")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật gần nhất")
    topics: Optional[list[TopicWithLesson]] = Field(
        None, description="Danh sách các chủ đề trong khóa học"
    )
    test_generation_status: str = Field(
        TestGenerationStatus.NOT_STARTED, description="Trạng thái tạo bài test đầu vào"
    )
    is_enrolled: Optional[bool] = Field(
        False, description="Trạng thái đăng ký của người dùng hiện tại"
    )

    @classmethod
    def from_model(cls, model):
        data = {}
        for field_name in cls.model_fields.keys():
            value = getattr(model, field_name, None)
            data[field_name] = value
        return cls(**data)

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    status : Optional[str] = None

    class Config:
        from_attributes = True


class CourseListItem(BaseModel):


    id: int = Field(..., description="ID của khóa học")
    title: str = Field(..., description="Tiêu đề của khóa học")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về khóa học")
    thumbnail_url: Optional[str] = Field(
        None, description="Đường dẫn đến ảnh thumbnail của khóa học"
    )
    level: Optional[str] = Field("Beginner", description="Cấp độ khó của khóa học")
    duration: Optional[int] = Field(
        0, description="Thời lượng ước tính để hoàn thành khóa học (tính bằng phút)"
    )
    price: Optional[float] = Field(0.0, description="Giá của khóa học (0 nếu miễn phí)")
    tags: Optional[str] = Field("", description="Các thẻ tag liên quan đến khóa học")
    created_at: datetime = Field(..., description="Thời điểm tạo khóa học")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật gần nhất")
    is_enrolled: Optional[bool] = Field(
        False, description="Trạng thái đăng ký của người dùng hiện tại"
    )

    @classmethod
    def from_model(cls, model):
        data = {}
        for field_name in cls.model_fields.keys():
            value = getattr(model, field_name, None)
            data[field_name] = value
        return cls(**data)

    class Config:
        from_attributes = True


class UserCourseListItem(BaseModel):

    id: int = Field(..., description="ID của khóa học")
    title: str = Field(..., description="Tiêu đề của khóa học")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về khóa học")
    thumbnail_url: Optional[str] = Field(
        None, description="Đường dẫn đến ảnh thumbnail của khóa học"
    )
    level: Optional[str] = Field("Beginner", description="Cấp độ khó của khóa học")
    duration: Optional[int] = Field(
        0, description="Thời lượng ước tính để hoàn thành khóa học (tính bằng phút)"
    )
    price: Optional[float] = Field(0.0, description="Giá của khóa học (0 nếu miễn phí)")
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
    created_at: datetime = Field(..., description="Thời điểm tạo khóa học")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật gần nhất")
    test_generation_status: str = Field(
        ..., description="Trạng thái tạo bài test đầu vào"
    )
    progress: float = Field(0.0, description="Phần trăm hoàn thành khóa học")
    current_topic_id: Optional[int] = Field(None, description="ID của chủ đề hiện tại")
    current_lesson_id: Optional[int] = Field(
        None, description="ID của bài học hiện tại"
    )

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    """
    Schema cho response khi lấy danh sách khóa học với phân trang

    Attributes:
        items: Danh sách các khóa học (chỉ thông tin cơ bản)
        total: Tổng số khóa học
        page: Số trang hiện tại
        limit: Số lượng item mỗi trang
        totalPages: Tổng số trang
    """

    items: list[CourseListItem]
    total: int
    page: int
    limit: int
    totalPages: int

    class Config:
        """Cấu hình cho Pydantic model"""

        from_attributes = True


# Rebuild model after TopicWithLessonsResponse is available
def rebuild_course_models():
    """Rebuild course models để resolve forward references"""
    try:
        CourseDetailResponse.model_rebuild()
    except Exception:
        pass


class CourseCompositionRequestSchema(BaseModel):
    lesson_id: Optional[int] = Field(
        None, description="ID của lesson hiện tại (nếu có), dùng để lấy context"
    )
    course_id: Optional[int] = Field(default=None, description="ID của khóa học")
    course_title: str = Field(..., description="Tiêu đề khóa học")
    course_description: str = Field(..., description="Mô tả khóa học")
    course_level: Optional[str] = Field(default="Beginner", description="Cấp độ khóa học")
    session_id: Optional[str] = Field(
        None, description="Session ID cho message history"
    )
    user_requirements: Optional[str] = Field(None, description="Yêu cầu của người dùng")
    max_topics: Optional[int] = Field(default=8, description="Số lượng topic tối đa")
    lessons_per_topic: Optional[int] = Field(default=5, description="Số lessons cho mỗi topic")


class TopicGenerationResult(BaseModel):
    name: str
    description: str
    prerequisites: Optional[List[str]] = None
    skills: List[str] = Field(
        ..., description="Danh sách kỹ năng đạt được sau khi học topic này"
    )
    order: int = Field(description="Thứ tự của topic trong khóa học")

    class Config:
        from_attributes = True


class CourseCompositionResponseSchema(BaseModel):
    topics: List[TopicGenerationResult] = Field(
        ..., description="Danh sách topics với skills"
    )
    duration: int = Field(
        ..., description="Thời gian ước lượng hoàn thành khóa học (giờ)"
    )
    description: str = Field(
        ..., description="Mô tả chi tiết về khóa học"
    )

    class Config:
        from_attributes = True


class BulkDeleteCoursesRequest(BaseModel):
    """Schema cho request xóa nhiều khóa học"""

    course_ids: list[int] = Field(..., description="Danh sách ID các khóa học cần xóa")

    @classmethod
    def validate_course_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Danh sách course_ids không được rỗng")
        return v


class BulkDeleteCoursesResponse(BaseModel):
    """Schema cho response xóa nhiều khóa học"""

    deleted_count: int = Field(..., description="Số lượng khóa học đã xóa thành công")
    failed_count: int = Field(..., description="Số lượng khóa học không thể xóa")
    errors: list[str] = Field(default_factory=list, description="Danh sách lỗi nếu có")
    deleted_courses: list[int] = Field(
        default_factory=list, description="Danh sách ID các khóa học đã xóa"
    )
    failed_courses: list[int] = Field(
        default_factory=list, description="Danh sách ID các khóa học không thể xóa"
    )
    deleted_items: dict[str, int] = Field(
        default_factory=dict,
        description="Thống kê chi tiết số lượng items đã xóa (courses, topics, lessons, lesson_sections)",
    )


class CourseDetailWithProgressResponse(CourseResponse):
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
    status: Optional[str] = None
    current_topic_id: Optional[int] = Field(None, description="Topic hiện tại đang học")
    current_lesson_id: Optional[int] = Field(
        None, description="Lesson hiện tại đang học"
    )
    current_lesson: Optional[dict] = Field(
        None, description="Chi tiết lesson hiện tại đang học"
    )
    last_activity_at: Optional[datetime] = Field(None, description="Hoạt động gần nhất")

    class Config:
        from_attributes = True
