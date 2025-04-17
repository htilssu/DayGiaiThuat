from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserStateBase(BaseModel):
    """
    Schema cơ bản cho trạng thái người dùng, chứa các trường cơ bản nhất
    """
    user_id: int
    streak_count: Optional[int] = Field(default=0)
    total_points: Optional[int] = Field(default=0)
    level: Optional[int] = Field(default=1)
    xp_to_next_level: Optional[int] = Field(default=100)
    daily_goal: Optional[int] = Field(default=30)
    daily_progress: Optional[int] = Field(default=0)

class UserStateCreate(UserStateBase):
    """
    Schema dùng để tạo trạng thái người dùng mới
    """
    current_course_id: Optional[int] = None
    current_lesson_id: Optional[int] = None
    preferences: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None

class UserStateUpdate(BaseModel):
    """
    Schema dùng để cập nhật trạng thái người dùng
    """
    last_active: Optional[datetime] = None
    current_course_id: Optional[int] = None
    current_lesson_id: Optional[int] = None
    streak_last_date: Optional[datetime] = None
    streak_count: Optional[int] = None
    total_points: Optional[int] = None
    level: Optional[int] = None
    xp_to_next_level: Optional[int] = None
    daily_goal: Optional[int] = None
    daily_progress: Optional[int] = None
    preferences: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None

class UserStateInDB(UserStateBase):
    """
    Schema đại diện cho trạng thái người dùng trong database
    """
    id: int
    last_active: datetime
    current_course_id: Optional[int] = None
    current_lesson_id: Optional[int] = None
    streak_last_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    preferences: Dict[str, Any]
    notifications: Dict[str, Any]
    
    class Config:
        from_attributes = True

class UserState(UserStateInDB):
    """
    Schema đầy đủ của trạng thái người dùng để trả về cho client
    """
    pass 