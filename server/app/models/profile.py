from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class Badge(BaseModel):
    """
    Mô hình dữ liệu cho huy hiệu người dùng
    
    Attributes:
        id (int): Mã định danh duy nhất của huy hiệu
        name (str): Tên hiển thị của huy hiệu
        icon (str): Biểu tượng emoji hoặc đường dẫn đến hình ảnh của huy hiệu
        description (str): Mô tả về cách đạt được huy hiệu
        unlocked (bool): Trạng thái mở khóa của huy hiệu
    """
    id: int
    name: str
    icon: str
    description: str
    unlocked: bool

class Activity(BaseModel):
    """
    Mô hình dữ liệu cho hoạt động của người dùng
    
    Attributes:
        id (int): Mã định danh duy nhất của hoạt động
        type (str): Loại hoạt động (exercise, course, discussion, badge)
        name (str): Tên hoạt động
        date (str): Ngày thực hiện hoạt động (định dạng dd/mm/yyyy)
        score (Optional[str]): Điểm số đạt được (nếu có)
        progress (Optional[str]): Tiến độ hoàn thành (nếu có)
    """
    id: int
    type: str
    name: str
    date: str
    score: Optional[str] = None
    progress: Optional[str] = None

class LearningProgress(BaseModel):
    """
    Mô hình dữ liệu cho tiến độ học tập của người dùng
    
    Attributes:
        algorithms (int): Tiến độ học thuật toán (0-100%)
        data_structures (int): Tiến độ học cấu trúc dữ liệu (0-100%)
        dynamic_programming (int): Tiến độ học quy hoạch động (0-100%)
    """
    algorithms: int = Field(default=0, ge=0, le=100)
    data_structures: int = Field(default=0, ge=0, le=100)
    dynamic_programming: int = Field(default=0, ge=0, le=100)

class CourseProgress(BaseModel):
    """
    Mô hình dữ liệu cho tiến độ khóa học
    
    Attributes:
        id (str): Mã định danh duy nhất của khóa học
        name (str): Tên khóa học
        progress (int): Tiến độ hoàn thành (0-100%)
        color_from (str): Mã màu bắt đầu cho gradient
        color_to (str): Mã màu kết thúc cho gradient
        image_url (Optional[str]): Đường dẫn đến hình ảnh khóa học (nếu có)
    """
    id: str
    name: str
    progress: int = Field(default=0, ge=0, le=100)
    color_from: str
    color_to: str
    image_url: Optional[str] = None

class UserStats(BaseModel):
    """
    Mô hình dữ liệu cho thống kê người dùng
    
    Attributes:
        completed_exercises (int): Số bài tập đã hoàn thành
        completed_courses (int): Số khóa học đã hoàn thành
        total_points (int): Tổng điểm đạt được
        streak_days (int): Số ngày hoạt động liên tiếp
        level (int): Cấp độ người dùng
        problems_solved (int): Số bài tập thuật toán đã giải
    """
    completed_exercises: int = 0
    completed_courses: int = 0
    total_points: int = 0
    streak_days: int = 0
    level: int = 1
    problems_solved: int = 0

class ProfileBase(BaseModel):
    """
    Mô hình dữ liệu cơ sở cho profile người dùng
    
    Attributes:
        full_name (Optional[str]): Họ và tên đầy đủ
        bio (Optional[str]): Giới thiệu ngắn về bản thân
        avatar_url (Optional[str]): Đường dẫn đến ảnh đại diện
    """
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileUpdate(ProfileBase):
    """
    Mô hình dữ liệu cho cập nhật profile người dùng
    """
    pass

class ProfileResponse(ProfileBase):
    """
    Mô hình dữ liệu cho phản hồi profile người dùng
    
    Attributes:
        id (str): Mã định danh người dùng
        username (str): Tên người dùng
        email (str): Địa chỉ email
        created_at (datetime): Thời điểm tạo tài khoản
        stats (UserStats): Thống kê người dùng
        badges (List[Badge]): Danh sách huy hiệu
        activities (List[Activity]): Lịch sử hoạt động
        learning_progress (LearningProgress): Tiến độ học tập
        courses (List[CourseProgress]): Danh sách khóa học đang theo dõi
    """
    id: str
    username: str
    email: str
    created_at: datetime
    stats: UserStats
    badges: List[Badge]
    activities: List[Activity]
    learning_progress: LearningProgress
    courses: List[CourseProgress]
    
    class Config:
        orm_mode = True
        
        
class ProfileInDB(ProfileResponse):
    """
    Mô hình dữ liệu cho profile người dùng trong database
    
    Attributes:
        user_id (str): Mã định danh người dùng trong database
        updated_at (datetime): Thời điểm cập nhật gần nhất
    """
    user_id: str
    updated_at: datetime
    
    class Config:
        orm_mode = True 