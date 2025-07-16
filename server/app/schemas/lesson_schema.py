from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.models.user_course_progress_model import ProgressStatus
from datetime import datetime


class LessonCompleteResponseSchema(BaseModel):
    lesson_id: int
    next_lesson_id: Optional[int] = None
    is_completed: bool


class ExerciseBase(BaseModel):
    """
    Schema cơ bản cho bài tập

    Attributes:
        name: Tên bài tập
        description: Mô tả chi tiết về bài tập
        difficulty: Độ khó của bài tập
        constraint: Các ràng buộc hoặc yêu cầu của bài tập
        suggest: Gợi ý để giải bài tập
    """

    name: str
    description: str
    difficulty: str
    constraint: Optional[str] = None
    suggest: Optional[str] = None


class ExerciseResponse(ExerciseBase):
    """
    Schema cho response khi truy vấn thông tin bài tập

    Attributes:
        id: ID của bài tập
        lesson_id: ID của bài học liên quan
    """

    id: int
    lesson_id: int


class LessonSectionResponse(BaseModel):
    """
    Schema cho phản hồi thông tin section của lesson
    """

    id: int
    type: str = Field(
        ..., description="Loại section: text, code, image, quiz, teaching"
    )
    content: str = Field(..., description="Nội dung của section")
    order: int = Field(..., description="Thứ tự section trong lesson")
    options: Optional[Dict[str, Any]] = Field(None, description="Tùy chọn cho quiz")
    answer: Optional[str] = Field(None, description="Đáp án đúng cho quiz (A, B, C, D)")
    explanation: Optional[str] = Field(None, description="Giải thích cho quiz")

    class Config:
        from_attributes = True


class Options(BaseModel):
    A: str
    B: str
    C: str
    D: str


class LessonSectionSchema(BaseModel):
    type: str  # "text", "code", "image", "quiz", "teaching"
    content: str
    order: int = Field(..., description="Thứ tự section trong lesson")
    options: Optional[Options] = Field(None, description="Tùy chọn cho quiz")
    answer: Optional[str] = Field(
        None,
        description="Đáp án đúng cho quiz nếu type là quiz",
    )
    explanation: Optional[str] = Field(
        None,
        description="Giải thích cho quiz nếu type là quiz",
    )


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
    sections: Optional[List[LessonSectionSchema]] = Field(
        None, description="Danh sách các section của lesson"
    )

    class Config:
        from_attributes = True


class CreateLessonSchema(BaseModel):
    external_id: str
    title: str
    description: str
    topic_id: int
    order: int
    next_lesson_id: Optional[str] = None
    prev_lesson_id: Optional[str] = None
    sections: List[LessonSectionSchema]


class UpdateLessonSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    next_lesson_id: Optional[str] = None
    prev_lesson_id: Optional[str] = None


class LessonResponseSchema(BaseModel):
    id: int
    external_id: str
    title: str
    description: str
    topic_id: int
    order: int
    next_lesson_id: Optional[str] = None
    prev_lesson_id: Optional[str] = None
    sections: List[LessonSectionSchema]
    exercises: List[ExerciseResponse] = []
    is_completed: Optional[bool] = False

    class Config:
        from_attributes = True


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


class GenerateLessonRequestSchema(BaseModel):
    topic_name: str
    lesson_title: str
    lesson_description: str
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    lesson_type: str = "theory"  # theory, practice, mixed
    include_examples: bool = True
    include_exercises: bool = True
    max_sections: int = 10
    session_id: Optional[str] = None
