"""
Module chứa các model của ứng dụng

Thứ tự import rất quan trọng để tránh circular dependency.
"""
# Import các model theo thứ tự phù hợp
from app.models.badge import Badge, user_badges
from app.models.course import Course
from app.models.user import User
from app.models.user_state import UserState
from app.models.learning_progress import LearningProgress

# Đảm bảo các model có thể được import từ app.models
__all__ = ["User", "Course", "Badge", "UserState", "LearningProgress", "user_badges"] 