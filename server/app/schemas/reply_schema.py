from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ReplyBase(BaseModel):
    """Base schema for reply data"""
    content: str


class ReplyCreate(ReplyBase):
    """Schema for creating a new reply"""
    discussion_id: int


class ReplyUpdate(BaseModel):
    """Schema for updating a reply"""
    content: Optional[str] = None


class ReplyResponse(ReplyBase):
    """Schema for reply response"""
    id: int
    discussion_id: int
    user_id: int
    author: str  # username of the author
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReplyListResponse(BaseModel):
    """Schema for reply list response"""
    replies: List[ReplyResponse]
    total: int

    class Config:
        from_attributes = True 