from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from app.schemas.auth import UserBase
from app.schemas.badge import Badge
from app.schemas.user_stats import UserStats, Activity, LearningProgress, CourseProgress

class UserUpdate(BaseModel):
    """
    Schema cho việc cập nhật thông tin người dùng
    
    Attributes:
        full_name (Optional[str]): Họ và tên đầy đủ
        bio (Optional[str]): Giới thiệu ngắn về bản thân
        avatar_url (Optional[str]): Đường dẫn đến ảnh đại diện
    """
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class User(UserBase):
    """
    Schema cho thông tin User trả về, kế thừa từ UserBase
    
    Attributes:
        id (int): ID của user
        is_active (bool): Trạng thái hoạt động của tài khoản
        created_at (datetime): Thời điểm tạo tài khoản
        updated_at (datetime): Thời điểm cập nhật gần nhất
        full_name (Optional[str]): Họ và tên đầy đủ
        bio (Optional[str]): Giới thiệu ngắn về bản thân
        avatar_url (Optional[str]): Đường dẫn đến ảnh đại diện
        stats (UserStats): Thống kê người dùng
        badges (List[Badge]): Danh sách huy hiệu
        activities (List[Activity]): Lịch sử hoạt động
        learning_progress (LearningProgress): Tiến độ học tập
        courses (List[CourseProgress]): Danh sách khóa học đang theo dõi
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    stats: UserStats
    badges: List[Badge] = []
    activities: List[Activity] = []
    learning_progress: LearningProgress
    courses: List[CourseProgress] = []

    class Config:
        from_attributes = True 