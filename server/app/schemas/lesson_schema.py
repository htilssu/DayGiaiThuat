from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LessonSectionResponse(BaseModel):
    """
    Schema cho phản hồi thông tin section của lesson
    """

    id: int
    type: str = Field(..., description="Loại section: text, code, image, quiz")
    content: str = Field(..., description="Nội dung của section")
    order: int = Field(..., description="Thứ tự section trong lesson")
    options: Optional[Dict[str, Any]] = Field(None, description="Tùy chọn cho quiz")
    answer: Optional[int] = Field(None, description="Đáp án đúng cho quiz")
    explanation: Optional[str] = Field(None, description="Giải thích cho quiz")

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    """
    Schema cho phản hồi thông tin lesson
    """

    id: int
    external_id: str = Field(..., description="ID hiển thị cho người dùng")
    title: str = Field(..., description="Tiêu đề lesson")
    description: str = Field(..., description="Mô tả lesson")
    topic_id: int = Field(..., description="ID của topic chứa lesson này")
    order: int = Field(..., description="Thứ tự lesson trong topic")
    next_lesson_id: Optional[str] = Field(None, description="ID lesson kế tiếp")
    prev_lesson_id: Optional[str] = Field(None, description="ID lesson trước đó")
    sections: List[LessonSectionResponse] = Field(
        default_factory=list, description="Danh sách sections"
    )

    class Config:
        from_attributes = True


class LessonWithProgressResponse(LessonResponse):
    """
    Schema cho lesson kèm thông tin tiến độ của user
    """

    is_completed: bool = Field(default=False, description="Lesson đã hoàn thành chưa")
    progress: int = Field(default=0, description="Tiến độ hoàn thành (0-100)")
    last_section_index: int = Field(default=0, description="Section cuối cùng đã xem")
    completed_at: Optional[datetime] = Field(None, description="Thời gian hoàn thành")

    class Config:
        from_attributes = True


def rebuild_lesson_models():
    """Rebuild lesson models để resolve forward references"""
    try:
        LessonResponse.model_rebuild()
        LessonSectionResponse.model_rebuild()
        LessonWithProgressResponse.model_rebuild()
    except Exception:
        pass
