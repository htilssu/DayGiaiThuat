from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DiscussionBase(BaseModel):
    """Base schema for discussion data"""
    title: str
    content: str
    category: str


class DiscussionCreate(DiscussionBase):
    """Schema for creating a new discussion"""
    pass


class DiscussionUpdate(BaseModel):
    """Schema for updating a discussion"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class DiscussionFilters(BaseModel):
    """Schema for discussion filters"""
    search: Optional[str] = None
    category: Optional[str] = None
    sort_by: Optional[str] = "newest"  # newest, oldest, most-replies
    page: Optional[int] = 1
    limit: Optional[int] = 10


class DiscussionResponse(DiscussionBase):
    """Schema for discussion response"""
    id: int
    user_id: int
    author: str  # username of the author
    replies_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiscussionListResponse(BaseModel):
    """Schema for paginated discussion list response"""
    discussions: List[DiscussionResponse]
    total: int
    page: int
    total_pages: int

    class Config:
        from_attributes = True 