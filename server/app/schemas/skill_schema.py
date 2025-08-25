from typing import Optional
from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    """Schema cơ bản cho Skill"""

    name: str = Field(..., description="Tên kỹ năng", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Mô tả chi tiết về kỹ năng")


class SkillCreate(SkillBase):
    """Schema để tạo mới Skill"""

    topic_id: int = Field(..., description="ID của topic mà kỹ năng này thuộc về")


class SkillUpdate(SkillBase):
    """Schema để cập nhật Skill"""


class SkillResponse(SkillBase):
    """Schema response cho Skill"""

    id: int = Field(..., description="ID của kỹ năng")
    topic_id: int = Field(..., description="ID của topic")

    class Config:
        from_attributes = True
