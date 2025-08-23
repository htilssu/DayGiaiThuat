from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.models.user_course_progress_model import ProgressStatus
from datetime import datetime


class LessonCompleteResponseSchema(BaseModel):
    lesson_id: Optional[int] = None
    next_lesson_id: Optional[int] = None
    is_completed: bool
    is_course_completed: bool = False


class BaseLesson(BaseModel):
    title: str
    description: str
    topic_id: int
    order: int

    class Config:
        from_attributes = True


class LessonResponseSchema(BaseLesson):
    id: int = Field(..., description="ID của lesson")
    is_completed: Optional[bool] = False


class ExerciseBase(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    difficulty: str
    estimated_time: Optional[str] = None
    completion_rate: Optional[int] = None
    completed: Optional[bool] = None
    content: Optional[str] = None
    executable: Optional[bool] = None
    code_template: Optional[str] = None

    class Config:
        from_attributes = True


class ExerciseResponse(ExerciseBase):
    id: int
    lesson_id: int


class LessonSectionAgentGenerated(BaseModel):
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


class LessonSectionSchema(LessonSectionAgentGenerated):
    id: int

    class Config:
        from_attributes = True


class Options(BaseModel):
    A: str
    B: str
    C: str
    D: str


class CreateLessonSchema(BaseLesson):
    sections: List[LessonSectionAgentGenerated]


class AgentCreateLessonSchema(CreateLessonSchema):
    exercises: List[ExerciseBase]


class UpdateLessonSchema(BaseLesson):
    pass


class LessonWithChildSchema(LessonResponseSchema):
    sections: List[LessonSectionSchema] = Field(
        default_factory=list, description="Danh sách các section của lesson"
    )
    exercises: List[ExerciseResponse] = Field(
        default_factory=list, description="Danh sách các bài tập của lesson"
    )

    class Config:
        from_attributes = True


class LessonWithProgressResponse(LessonWithChildSchema):
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
    difficulty_level: str = "beginner"
    lesson_type: str = "theory"
    include_examples: bool = True
    include_exercises: bool = True
    max_sections: int = 10
    session_id: Optional[str] = None
