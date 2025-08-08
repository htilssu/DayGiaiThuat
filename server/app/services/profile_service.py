from typing import Dict, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database.database import get_async_db
from ..models import (
    Badge,
    User,
    UserBadge,
    UserCourse,
    Course,
    UserCourseProgress,
)
from ..models.user_course_progress_model import ProgressStatus


class ProfileService:
    """
    Service xử lý các yêu cầu liên quan đến profile người dùng
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Lấy thông tin profile đầy đủ của người dùng
        """
        # Lấy thông tin cơ bản của người dùng
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("Người dùng không tồn tại")

        # Lấy danh sách khóa học đã đăng ký với progress
        enrolled_courses_result = await self.db.execute(
            select(Course, UserCourse)
            .join(UserCourse, UserCourse.course_id == Course.id)
            .where(UserCourse.user_id == user_id)
        )
        enrolled_courses = enrolled_courses_result.all()

        # Lấy danh sách huy hiệu
        badges_result = await self.db.execute(
            select(Badge, UserBadge)
            .outerjoin(
                UserBadge,
                (UserBadge.badge_id == Badge.id) & (UserBadge.user_id == user_id),
            )
        )
        badges = badges_result.all()

        # Tạo dữ liệu mẫu cho các phần còn thiếu (trong thực tế sẽ lấy từ DB)
        # TODO: Thay thế bằng dữ liệu thực từ database
        stats = {
            "level": 3,
            "completed_exercises": 24,
            "completed_courses": 2,
            "total_points": 1250,
            "streak_days": 7,
            "problems_solved": 15,
        }

        learning_progress = {
            "algorithms": 65,
            "data_structures": 40,
            "dynamic_programming": 25,
        }

        activities = [
            {
                "id": 1,
                "name": "Hoàn thành bài tập Tìm kiếm nhị phân",
                "type": "exercise",
                "date": "15/10/2023",
                "score": "95",
            },
            {
                "id": 2,
                "name": "Bắt đầu khóa học Cấu trúc dữ liệu",
                "type": "course",
                "date": "10/10/2023",
                "progress": "25%",
            },
            {
                "id": 3,
                "name": "Tham gia thảo luận về Thuật toán sắp xếp",
                "type": "discussion",
                "date": "05/10/2023",
            },
        ]

        # Chuyển đổi dữ liệu khóa học
        courses = []
        for course, user_course in enrolled_courses:
            # Tính progress dựa trên UserCourseProgress
            # First get total lessons
            total_result = await self.db.execute(
                select(func.count())
                .select_from(UserCourseProgress)
                .where(UserCourseProgress.user_course_id == user_course.id)
            )
            total_lessons = total_result.scalar() or 0
            
            # Then get completed lessons
            completed_result = await self.db.execute(
                select(func.count())
                .select_from(UserCourseProgress)
                .where(
                    UserCourseProgress.user_course_id == user_course.id,
                    UserCourseProgress.status == ProgressStatus.COMPLETED
                )
            )
            completed_lessons = completed_result.scalar() or 0
            
            # Calculate progress percentage
            progress = int((completed_lessons / total_lessons * 100) if total_lessons > 0 else 0)
            
            courses.append(
                {
                    "id": str(course.id),
                    "name": course.title,
                    "progress": progress,
                    "color_from": "blue-500",  # Màu mặc định
                    "color_to": "indigo-600",  # Màu mặc định
                }
            )

        # Chuyển đổi dữ liệu huy hiệu
        badge_list = []
        for badge, user_badge in badges:
            # UserBadge tồn tại có nghĩa là user đã có huy hiệu này
            has_badge = user_badge is not None
            badge_list.append(
                {
                    "id": badge.id,
                    "name": badge.name,
                    "icon": badge.icon or "🏆",
                    "description": badge.description,
                    "unlocked": has_badge,
                }
            )

        # Tạo response
        return {
            "id": user.id,
            "username": user.username,
            "fullName": user.full_name or f"{user.first_name or ''} {user.last_name or ''}".strip() or "Unknown User",
            "email": user.email,
            "avatar": user.avatar,
            "bio": user.bio or "Chưa có thông tin giới thiệu",
            "stats": stats,
            "learningProgress": learning_progress,
            "courses": courses,
            "badges": badge_list,
            "activities": activities,
        }


def get_profile_service(db: AsyncSession = Depends(get_async_db)) -> ProfileService:
    """
    Dependency để inject ProfileService
    """
    return ProfileService(db)
