from typing import List, Optional
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
    prerequisites: Optional[List[str]] = Field(None, description="Danh sách các điều kiện tiên quyết")


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
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên chủ đề")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về chủ đề")
    prerequisites: Optional[List[str]] = Field(None, description="Danh sách các điều kiện tiên quyết")
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
