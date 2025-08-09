from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.auth_schema import UserBase
from app.schemas.badge_schema import Badge
from app.schemas.user_stats_schema import (
    UserStats,
    Activity,
    LearningProgress,
    CourseProgress,
)


class ProfileBadge(BaseModel):
    """
    Schema cho huy hiệu trong profile response
    """
    id: int
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    unlocked: bool = False

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """
    Schema cho việc cập nhật thông tin người dùng

    Attributes:
        first_name (Optional[str]): Tên của người dùng
        last_name (Optional[str]): Họ của người dùng
        bio (Optional[str]): Giới thiệu ngắn về bản thân
        avatar_url (Optional[str]): Đường dẫn đến ảnh đại diện
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
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
        first_name (Optional[str]): Tên của người dùng
        last_name (Optional[str]): Họ của người dùng
        bio (Optional[str]): Giới thiệu ngắn về bản thân
        avatar_url (Optional[str]): Đường dẫn đến ảnh đại diện
        stats (UserStats): Thống kê người dùng
        badges (List[Badge]): Danh sách huy hiệu
        activities (List[Activity]): Lịch sử hoạt động
        learning_progress (LearningProgress): Tiến độ học tập
        course_progress (List[CourseProgress]): Danh sách khóa học đang theo dõi
    """

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    stats: UserStats
    badges: List[Badge] = []
    activities: List[Activity] = []
    learning_progresses: LearningProgress
    course_progress: List[CourseProgress] = []

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


class UserExcludeSecret(BaseModel):
    """
    Schema cho thông tin User trả về, không bao gồm mật khẩu

    Attributes:
        id (int): ID của user
        email (str): Email của user
        username (str): Tên đăng nhập của user
        is_active (bool): Trạng thái hoạt động của tài khoản
        is_admin (bool): Quyền admin của user
        created_at (datetime): Thời điểm tạo tài khoản
        updated_at (datetime): Thời điểm cập nhật gần nhất
    """

    id: int
    email: str
    username: Optional[str] = None
    is_active: bool
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: int
    username: str
    fullName: str
    email: str
    avatar: Optional[str] = None
    bio: str
    stats: UserStats
    learningProgress: LearningProgress
    courses: List[CourseProgress]
    badges: List[ProfileBadge]
    activities: List[Activity]

    class Config:
        from_attributes = True
