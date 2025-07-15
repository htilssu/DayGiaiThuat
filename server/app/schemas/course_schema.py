from datetime import datetime
from typing import List, Optional

from app.models.course_model import TestGenerationStatus
from app.models.user_course_progress_model import ProgressStatus
from app.schemas.topic_schema import TopicResponse
from pydantic import BaseModel, Field


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
    topics: Optional[list[TopicResponse]] = Field(
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

    topics: list["TopicResponse"] = Field(
        default_factory=list, description="Danh sách topics và lessons"
    )

    class Config:
        from_attributes = True


class CourseListItem(BaseModel):
    """
    Schema cơ bản cho item trong danh sách khóa học (không bao gồm chi tiết topics)

    Attributes:
        id: ID của khóa học
        title: Tiêu đề của khóa học
        description: Mô tả chi tiết về khóa học
        thumbnail_url: Đường dẫn đến ảnh thumbnail của khóa học
        level: Cấp độ khó của khóa học
        duration: Thời lượng ước tính để hoàn thành khóa học (tính bằng phút)
        price: Giá của khóa học (0 nếu miễn phí)
        tags: Các thẻ tag liên quan đến khóa học
        created_at: Thời điểm tạo khóa học
        updated_at: Thời điểm cập nhật gần nhất
        is_enrolled: Trạng thái đăng ký của người dùng hiện tại (chỉ có khi người dùng đã đăng nhập)
    """

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


# Rebuild model after TopicWithLessonsResponse is available
def rebuild_course_models():
    """Rebuild course models để resolve forward references"""
    try:
        CourseDetailResponse.model_rebuild()
    except Exception:
        pass


class CourseCompositionRequestSchema(BaseModel):
    """Schema cho request tạo khóa học tự động"""

    course_id: int = Field(..., description="ID của khóa học")
    course_title: str = Field(..., description="Tiêu đề khóa học")
    course_description: str = Field(..., description="Mô tả khóa học")
    course_level: str = Field(..., description="Cấp độ khóa học")
    max_topics: int = Field(default=10, description="Số lượng topic tối đa")
    lessons_per_topic: int = Field(default=5, description="Số lessons cho mỗi topic")


class TopicGenerationResult(BaseModel):
    """Kết quả tạo topic"""

    name: str
    description: str
    prerequisites: Optional[List[str]] = None
    order: int


class CourseCompositionResponseSchema(BaseModel):
    """Schema cho response của CourseCompositionAgent"""

    course_id: int
    topics: List[TopicResponse]
    status: str
    errors: List[str]


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


class LessonWithProgressResponse(BaseModel):
    """
    Schema cho lesson với thông tin progress
    """

    id: int = Field(..., description="ID của lesson")
    external_id: str = Field(..., description="External ID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    description: str = Field(..., description="Mô tả lesson")
    order: int = Field(..., description="Thứ tự lesson trong topic")

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

    class Config:
        from_attributes = True


class TopicWithProgressResponse(BaseModel):
    """
    Schema cho topic với lessons và progress nested
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
    """

    id: int = Field(..., description="ID của lesson")
    external_id: str = Field(..., description="External ID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    description: str = Field(..., description="Mô tả lesson")
    order: int = Field(..., description="Thứ tự lesson trong topic")
    topic_id: int = Field(..., description="ID của topic")

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
