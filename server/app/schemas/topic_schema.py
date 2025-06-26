from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên chủ đề")
    description: Optional[str] = Field(None, description="Mô tả chủ đề")
    course_id: int = Field(..., description="ID của khóa học chứa chủ đề này")


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


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
    course_id: int
    user_topic_state: Optional[UserTopic]

    class Config:
        from_attributes = True
