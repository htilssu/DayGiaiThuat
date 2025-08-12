from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.core.agents.test_generate_agent import Question
from app.database.mongodb import PyObjectId
from app.schemas import LessonSummary, LessonSectionSchema
from app.schemas.test_schema import TestBase
from app.schemas.topic_schema import TopicBase


class BaseSchemaNoAlias(BaseModel):
    def model_dump(self, **kwargs):
        return super().model_dump(by_alias=False, **kwargs)

    def model_dump_json(self, **kwargs):
        return super().model_dump_json(by_alias=False, **kwargs)


class LessonDraft(LessonSummary, BaseSchemaNoAlias):
    id: PyObjectId = Field(..., description="ID của bài học", )
    sections: List[LessonSectionSchema] = Field(
        default_factory=list, description="Danh sách các phần trong bài học")

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class SkillDraft(BaseSchemaNoAlias):
    id: PyObjectId = Field(..., description="ID của kỹ năng", )
    name: str = Field(..., description="Tên kỹ năng")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về kỹ năng")

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class TestDraft(TestBase, BaseSchemaNoAlias):
    questions: List[Question] = Field(default_factory=list, description="Danh sách các câu hỏi trong bài kiểm tra")
    id: PyObjectId = Field(..., description="ID của bài kiểm tra", )

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class TopicDraftSchema(TopicBase, BaseSchemaNoAlias):
    id: PyObjectId = Field(..., description="ID của chủ đề")
    lessons: List[LessonDraft] = Field(
        default_factory=list, description="Danh sách các bài học trong chủ đề")
    skills: List[SkillDraft] = Field(
        default_factory=list, description="Danh sách các kỹ năng liên quan đến chủ đề")
    tests: List[TestDraft] = Field(
        default_factory=list, description="Danh sách các bài kiểm tra liên quan đến chủ đề")
    order: Optional[int] = Field(
        None, description="Thứ tự của chủ đề trong khóa học (nếu có)")

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class CourseDraftSchemaNoId(BaseSchemaNoAlias):
    duration: int = Field(..., description="Thời gian ước lượng hoàn thành khóa học (số nguyên, đơn vị giờ)")
    description: str = Field(..., description="Mô tả chi tiết về khóa học")
    session_id: str = Field(..., description="ID của phiên làm việc khóa học")
    topics: list[TopicDraftSchema] = Field(
        ...,
        description="Danh sách các chủ đề trong khóa học, mỗi chủ đề bao gồm tên, mô tả, kiến thức tiên quyết và kỹ năng",
    )

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class CourseDraftSchema(CourseDraftSchemaNoId):
    id: PyObjectId = Field(..., description="Id của schema khóa học đã soạn thảo", )
    course_id: int = Field(..., description="ID của khóa học liên kết với schema này")
