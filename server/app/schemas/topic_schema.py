from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.lesson_schema import (
    LessonSummary,
    LessonWithChildSchema,
    LessonDetailWithProgressResponse,
)
from app.schemas.skill_schema import SkillBase


class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên chủ đề")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về chủ đề")
    prerequisites: Optional[List[str]] = Field(
        None, description="Danh sách các điều kiện tiên quyết"
    )

    class Config:
        from_attributes = True


class TopicHasSkill(TopicBase):
    skills: list[SkillBase] = Field(
        default_factory=list, description="Danh sách các kỹ năng liên quan đến chủ đề"
    )


class TopicForTestGenerateAgent(TopicHasSkill):
    lessons: List[LessonSummary]


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
        order: Thứ tự của chủ đề trong khóa học
        created_at: Thời điểm tạo
        updated_at: Thời điểm cập nhật
    """

    id: int = Field(..., description="ID của chủ đề")
    external_id: Optional[str] = Field(None, description="ID hiển thị cho người dùng")
    course_id: Optional[int] = Field(
        None, description="ID của khóa học chứa chủ đề này"
    )
    order: Optional[int] = Field(None, description="Thứ tự của chủ đề trong khóa học")
    is_completed: Optional[bool] = Field(
        None, description="Trạng thái hoàn thành của chủ đề"
    )
    progress: Optional[int] = Field(
        None, description="Tiến trình hoàn thành của chủ đề"
    )
    completed_lessons: Optional[int] = Field(
        None, description="Số lượng lessons đã hoàn thành của chủ đề"
    )
    created_at: datetime = Field(..., description="Thời điểm tạo")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật")
    lessons: List[LessonWithChildSchema] = Field(
        default_factory=list, description="Danh sách lessons"
    )

    class Config:
        from_attributes = True


class TopicWithLessonsResponse(TopicResponse):
    """
    Schema cho response topic kèm lessons
    """

    lessons: List[LessonWithChildSchema] = Field(
        default_factory=list, description="Danh sách lessons"
    )

    class Config:
        from_attributes = True


class TopicCreate(TopicBase):
    """Schema cho việc tạo topic (admin)"""

    course_id: Optional[int] = Field(
        None, description="ID của khóa học chứa chủ đề này (có thể null)"
    )


class TopicUpdate(BaseModel):
    """Schema cho việc cập nhật topic (admin)"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: Optional[int] = None


class TopicCourseAssignment(BaseModel):
    """Schema cho việc gán topic vào course"""

    course_id: Optional[int] = Field(
        None, description="ID của khóa học (null để unassign)"
    )


class UserTopic(BaseModel):
    """Schema cho trạng thái topic của user"""

    user_id: int
    topic_id: int
    completed: bool
    is_unlocked: bool
    unlocked_at: Optional[datetime]

    class Config:
        from_attributes = True


class TopicWithUserState(BaseModel):
    """Schema cho topic với trạng thái user"""

    id: int
    name: str
    description: Optional[str]
    course_id: Optional[int]
    user_topic_state: Optional[UserTopic]

    class Config:
        from_attributes = True


class TopicWithProgressResponse(BaseModel):
    id: int = Field(..., description="ID của topic")
    external_id: Optional[str] = Field(None, description="External ID của topic")
    name: str = Field(..., description="Tên topic")
    description: str = Field(..., description="Mô tả topic")
    order: Optional[int] = Field(None, description="Thứ tự topic trong course")

    lessons: List[LessonDetailWithProgressResponse] = Field(
        default=[], description="Danh sách lessons với progress"
    )

    topic_completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành topic"
    )
    completed_lessons: int = Field(default=0, description="Số lesson đã hoàn thành")
    total_lessons: int = Field(default=0, description="Tổng số lesson trong topic")

    class Config:
        from_attributes = True


class TopicDetailWithProgressResponse(BaseModel):
    id: int = Field(..., description="ID của topic")
    external_id: Optional[str] = Field(None, description="External ID của topic")
    name: str = Field(..., description="Tên topic")
    description: str = Field(..., description="Mô tả topic")
    order: Optional[int] = Field(None, description="Thứ tự topic trong course")
    course_id: Optional[int] = Field(None, description="ID của course")

    lessons: List[LessonDetailWithProgressResponse] = Field(
        default=[], description="Danh sách lessons với progress"
    )

    topic_completion_percentage: float = Field(
        default=0.0, description="Phần trăm hoàn thành topic"
    )
    completed_lessons: int = Field(default=0, description="Số lesson đã hoàn thành")
    total_lessons: int = Field(default=0, description="Tổng số lesson trong topic")

    user_course_id: Optional[int] = Field(
        None, description="ID của user course nếu đã đăng ký"
    )

    class Config:
        from_attributes = True
