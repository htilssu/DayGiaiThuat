from typing import Dict, Any

from fastapi import Depends
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..models import (
    Badge,
    User,
    UserBadge,
    UserCourse,
    Course,
)


class ProfileService:
    """
    Service xử lý các yêu cầu liên quan đến profile người dùng
    """

    def __init__(self, db: Session):
        self.db = db

    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Lấy thông tin profile đầy đủ của người dùng
        """
        # Lấy thông tin cơ bản của người dùng
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Người dùng không tồn tại")

        # Lấy danh sách khóa học đã đăng ký
        enrolled_courses = (
            self.db.query(Course, UserCourse.progress)
            .join(UserCourse, UserCourse.course_id == Course.id)
            .filter(UserCourse.user_id == user_id)
            .all()
        )

        # Lấy danh sách huy hiệu
        badges = (
            self.db.query(Badge, UserBadge.unlocked)
            .outerjoin(
                UserBadge,
                (UserBadge.badge_id == Badge.id) & (UserBadge.user_id == user_id),
            )
            .all()
        )

        # Tạo dữ liệu mẫu cho các phần còn thiếu (trong thực tế sẽ lấy từ DB)
        # TODO: Thay thế bằng dữ liệu thực từ database
        stats = {
            "level": 3,
            "completedExercises": 24,
            "completedCourses": 2,
            "totalPoints": 1250,
            "streak": 7,
        }

        learning_progress = {
            "algorithms": 65,
            "dataStructures": 40,
            "dynamicProgramming": 25,
        }

        activities = [
            {
                "id": 1,
                "name": "Hoàn thành bài tập Tìm kiếm nhị phân",
                "type": "exercise",
                "date": "2023-10-15",
                "score": 95,
            },
            {
                "id": 2,
                "name": "Bắt đầu khóa học Cấu trúc dữ liệu",
                "type": "course",
                "date": "2023-10-10",
                "progress": "25%",
            },
            {
                "id": 3,
                "name": "Tham gia thảo luận về Thuật toán sắp xếp",
                "type": "discussion",
                "date": "2023-10-05",
            },
        ]

        # Chuyển đổi dữ liệu khóa học
        courses = []
        for course, progress in enrolled_courses:
            courses.append(
                {
                    "id": course.id,
                    "name": course.title,
                    "progress": progress or 0,
                    "color_from": "blue-500",  # Màu mặc định
                    "color_to": "indigo-600",  # Màu mặc định
                }
            )

        # Chuyển đổi dữ liệu huy hiệu
        badge_list = []
        for badge, unlocked in badges:
            badge_list.append(
                {
                    "id": badge.id,
                    "name": badge.name,
                    "icon": badge.icon or "🏆",
                    "description": badge.description,
                    "unlocked": bool(unlocked),
                }
            )

        # Tạo response
        return {
            "id": user.id,
            "username": user.username,
            "fullName": user.fullname,
            "email": user.email,
            "avatar": user.avatar,
            "bio": user.bio or "Chưa có thông tin giới thiệu",
            "stats": stats,
            "learningProgress": learning_progress,
            "courses": courses,
            "badges": badge_list,
            "activities": activities,
        }


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    """
    Dependency để inject ProfileService
    """
    return ProfileService(db)
