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
    sortBy: Optional[str] = "newest"  # newest, oldest, most-replies
    page: Optional[int] = 1
    limit: Optional[int] = 10


class DiscussionResponse(DiscussionBase):
    """Schema for discussion response"""
    id: int
    author: str  # username of the author
    replies: int
    createdAt: str  # ISO string for frontend compatibility
    updatedAt: str

    class Config:
        from_attributes = True


class DiscussionListResponse(BaseModel):
    """Schema for paginated discussion list response"""
    discussions: List[DiscussionResponse]
    total: int
    page: int
    totalPages: int

    class Config:
        from_attributes = True 