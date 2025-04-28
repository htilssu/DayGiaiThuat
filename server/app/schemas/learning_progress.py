from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class LearningProgressBase(BaseModel):
    """
    Schema cơ bản cho tiến độ học tập, chứa các trường cơ bản nhất
    """
    user_id: int
    course_id: int
    progress_percent: Optional[float] = Field(default=0.0)
    is_completed: Optional[bool] = Field(default=False)
    notes: Optional[str] = None
    favorite: Optional[bool] = Field(default=False)

class LearningProgressCreate(LearningProgressBase):
    """
    Schema dùng để tạo tiến độ học tập mới
    """
    completed_lessons: Optional[List[int]] = Field(default_factory=list)
    quiz_scores: Optional[Dict[str, Any]] = Field(default_factory=dict)

class LearningProgressUpdate(BaseModel):
    """
    Schema dùng để cập nhật tiến độ học tập
    """
    progress_percent: Optional[float] = None
    is_completed: Optional[bool] = None
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None
    favorite: Optional[bool] = None
    completed_lessons: Optional[List[int]] = None
    quiz_scores: Optional[Dict[str, Any]] = None

class LearningProgressInDB(LearningProgressBase):
    """
    Schema đại diện cho tiến độ học tập trong database
    """
    id: int
    last_accessed: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    completed_lessons: List[int]
    quiz_scores: Dict[str, Any]
    
    class Config:
        from_attributes = True

class LearningProgress(LearningProgressInDB):
    """
    Schema đầy đủ của tiến độ học tập để trả về cho client
    """
    pass

class LearningProgressList(BaseModel):
    """
    Schema danh sách tiến độ học tập
    """
    progress_items: List[LearningProgress]
    total: int 