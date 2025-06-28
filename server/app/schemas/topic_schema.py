from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.lesson_schema import LessonResponseSchema


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


class CreateTopicSchema(TopicBase):
    """
    Schema cho việc tạo mới chủ đề

    Attributes:
        course_id: ID của khóa học chứa chủ đề này
        external_id: ID hiển thị cho người dùng (tùy chọn)
    """

    course_id: int = Field(..., description="ID của khóa học chứa chủ đề này")
    external_id: Optional[str] = Field(None, description="ID hiển thị cho người dùng")


class UpdateTopicSchema(BaseModel):
    """
    Schema cho việc cập nhật chủ đề

    Note:
        Các trường đều là Optional vì khi cập nhật không nhất thiết phải cung cấp tất cả các trường.
    """

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Tên chủ đề"
    )
    description: Optional[str] = Field(None, description="Mô tả chi tiết về chủ đề")
    prerequisites: Optional[List[str]] = Field(
        None, description="Danh sách các điều kiện tiên quyết"
    )
    external_id: Optional[str] = Field(None, description="ID hiển thị cho người dùng")


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


class TopicWithLessonsResponse(TopicResponse):
    lessons: List[LessonResponseSchema] = []

    class Config:
        from_attributes = True


if TYPE_CHECKING:
    from app.schemas.lesson_schema import LessonResponseSchema


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
