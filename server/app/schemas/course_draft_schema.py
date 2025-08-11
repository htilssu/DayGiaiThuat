from bson import ObjectId
from pydantic import BaseModel, Field

from app.schemas.topic_schema import TopicBase


class CourseDraftSchema(BaseModel):
    duration: int = Field(..., description="Thời gian ước lượng hoàn thành khóa học (số nguyên, đơn vị giờ)")
    description: str = Field(..., description="Mô tả chi tiết về khóa học")
    topics: list[TopicBase] = Field(
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


class CourseDraftSchemaWithId(CourseDraftSchema):
    """
    Schema cho khóa học đã soạn thảo, bao gồm ID
    """
    id: str = Field(..., description="Id của schema khóa học đã soạn thảo", alias="_id")
    course_id: int = Field(..., description="ID của khóa học liên kết với schema này")


class CourseDraftReviewSchema(CourseDraftSchemaWithId):
    pass