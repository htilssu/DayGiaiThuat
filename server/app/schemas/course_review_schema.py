from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CourseDraftResponse(BaseModel):
    """Schema cho response của course draft"""
    id: int
    course_id: int
    agent_content: str  # JSON string chứa topics, lessons
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CourseReviewChatMessage(BaseModel):
    """Schema cho tin nhắn chat trong quá trình review"""
    id: int
    course_id: int
    user_id: int
    message: str
    is_agent: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SendChatMessageRequest(BaseModel):
    """Schema cho request gửi tin nhắn chat"""
    message: str

class CourseReviewResponse(BaseModel):
    """Schema cho response của trang review course"""
    course_id: int
    course_title: str
    course_description: str
    draft: Optional[CourseDraftResponse]
    chat_messages: List[CourseReviewChatMessage]

class ApproveDraftRequest(BaseModel):
    """Schema cho request approve draft"""
    approved: bool
    feedback: Optional[str] = None
