from app.models.user import User
from app.models.course import Course
from app.models.learning_progress import LearningProgress
from app.models.badge import Badge, user_badges
from app.models.user_state import UserState

# Đảm bảo tất cả các model được import để Alembic có thể nhận diện
__all__ = [
    "User",
    "Course",
    "LearningProgress",
    "Badge",
    "UserState",
    "user_badges"
] 