from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class CourseBase(BaseModel):
    """
    Schema cơ bản cho khóa học, chứa các trường cơ bản nhất
    """
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    level: Optional[str] = Field(default="Beginner")
    duration: Optional[int] = Field(default=0)
    price: Optional[float] = Field(default=0.0)
    tags: Optional[str] = Field(default="")
    
class CourseCreate(CourseBase):
    """
    Schema dùng để tạo khóa học mới
    """
    requirements: Optional[str] = None
    what_you_will_learn: Optional[str] = None
    is_published: Optional[bool] = Field(default=False)

class CourseUpdate(CourseBase):
    """
    Schema dùng để cập nhật khóa học
    """
    title: Optional[str] = None
    requirements: Optional[str] = None
    what_you_will_learn: Optional[str] = None
    is_published: Optional[bool] = None

class CourseInDB(CourseBase):
    """
    Schema đại diện cho khóa học trong database
    """
    id: int
    requirements: Optional[str] = None
    what_you_will_learn: Optional[str] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Course(CourseInDB):
    """
    Schema đầy đủ của khóa học để trả về cho client
    """
    pass

class CourseList(BaseModel):
    """
    Schema danh sách khóa học
    """
    courses: List[Course]
    total: int