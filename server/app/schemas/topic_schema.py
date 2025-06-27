from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field

# Import LessonResponse directly for runtime
try:
    from app.schemas.lesson_schema import LessonResponse
except ImportError:
    # Fallback for circular import issues
    LessonResponse = None

if TYPE_CHECKING:
    from app.schemas.lesson_schema import LessonResponse


class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên chủ đề")
    description: Optional[str] = Field(None, description="Mô tả chủ đề")
    course_id: Optional[int] = Field(
        None, description="ID của khóa học chứa chủ đề này (có thể null)"
    )


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: Optional[int] = None


class TopicCourseAssignment(BaseModel):
    course_id: Optional[int] = Field(
        None, description="ID của khóa học (null để unassign)"
    )


class TopicResponse(TopicBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserTopic(BaseModel):
    user_id: int
    topic_id: int
    completed: bool
    is_unlocked: bool
    unlocked_at: Optional[datetime]

    class Config:
        from_attributes = True


class TopicWithUserState(BaseModel):
    id: int
    name: str
    description: Optional[str]
    course_id: Optional[int]
    user_topic_state: Optional[UserTopic]

    class Config:
        from_attributes = True


class TopicWithLessonsResponse(TopicResponse):
    """
    Schema cho topic bao gồm cả danh sách lessons
    """

    lessons: List["LessonResponse"] = Field(
        default_factory=list, description="Danh sách lessons"
    )

    class Config:
        from_attributes = True


# Rebuild model after LessonResponse is available
def rebuild_models():
    """Rebuild models để resolve forward references"""
    try:
        TopicWithLessonsResponse.model_rebuild()
    except Exception:
        pass
