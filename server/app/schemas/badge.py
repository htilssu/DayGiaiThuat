from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class BadgeBase(BaseModel):
    """
    Schema cơ bản cho huy hiệu, chứa các trường cơ bản nhất
    """
    name: str
    icon: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = Field(default="Achievement")
    criteria: Optional[str] = None
    points: Optional[int] = Field(default=0)
    rarity: Optional[str] = Field(default="Common")
    
class BadgeCreate(BadgeBase):
    """
    Schema dùng để tạo huy hiệu mới
    """
    is_hidden: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=True)

class BadgeUpdate(BadgeBase):
    """
    Schema dùng để cập nhật huy hiệu
    """
    name: Optional[str] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    criteria: Optional[str] = None
    points: Optional[int] = None
    rarity: Optional[str] = None
    is_hidden: Optional[bool] = None
    is_active: Optional[bool] = None

class BadgeInDB(BadgeBase):
    """
    Schema đại diện cho huy hiệu trong database
    """
    id: int
    is_hidden: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Badge(BadgeInDB):
    """
    Schema đầy đủ của huy hiệu để trả về cho client
    """
    pass

class UserBadge(BaseModel):
    """
    Schema cho huy hiệu của người dùng
    """
    badge: Badge
    earned_at: datetime
    is_featured: bool
    
    class Config:
        from_attributes = True

class BadgeList(BaseModel):
    """
    Schema danh sách huy hiệu
    """
    badges: List[Badge]
    total: int 