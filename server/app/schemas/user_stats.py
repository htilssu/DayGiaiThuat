from typing import Optional

from pydantic import BaseModel


class Activity(BaseModel):
    """
    Schema cho hoạt động của người dùng
    
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


class UserStats(BaseModel):
    """
    Schema cho thống kê người dùng
    
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


class LearningProgress(BaseModel):
    """
    Schema cho tiến độ học tập của người dùng
    
    Attributes:
        algorithms (int): Tiến độ học thuật toán (0-100%)
        data_structures (int): Tiến độ học cấu trúc dữ liệu (0-100%)
        dynamic_programming (int): Tiến độ học quy hoạch động (0-100%)
    """
    algorithms: int = 0
    data_structures: int = 0
    dynamic_programming: int = 0


class CourseProgress(BaseModel):
    """
    Schema cho tiến độ khóa học
    
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
    progress: int = 0
    color_from: str
    color_to: str
    image_url: Optional[str] = None
