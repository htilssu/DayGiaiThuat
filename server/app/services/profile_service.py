from typing import Dict, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..database.database import get_async_db
from ..models import (
    Badge,
    User,
    UserBadge,
    UserCourse,
    Course,
    UserCourseProgress,
    UserState,
    UserActivity,
    UserTopicProgress,
    Topic,
)
from ..models.user_course_progress_model import ProgressStatus
from ..models.user_activity_model import ActivityType


class ProfileService:
    """
    Service xử lý các yêu cầu liên quan đến profile người dùng
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Lấy thông tin profile đầy đủ của người dùng từ dữ liệu thực trong database
        """
        # Lấy thông tin cơ bản của người dùng với user state
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.state))
            .where(User.id == user_id)
        )
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

        # Lấy thống kê thực từ UserState
        user_state = user.state
        if user_state:
            stats = {
                "level": user_state.level,
                "completedExercises": user_state.completed_exercises,
                "completedCourses": user_state.completed_courses,
                "totalPoints": user_state.total_points,
                "streak": user_state.streak_count,
                "problems_solved": user_state.problems_solved,
            }
        else:
            # Nếu chưa có UserState, tạo thống kê mặc định
            stats = {
                "level": 1,
                "completedExercises": 0,
                "completedCourses": 0,
                "totalPoints": 0,
                "streak": 0,
                "problems_solved": 0,
            }

        # Lấy tiến độ học tập theo chủ đề từ UserTopicProgress
        topic_progress_result = await self.db.execute(
            select(UserTopicProgress, Topic)
            .join(Topic, Topic.id == UserTopicProgress.topic_id)
            .where(UserTopicProgress.user_id == user_id)
        )
        topic_progress_data = topic_progress_result.all()

        # Tạo dictionary tiến độ học tập
        learning_progress = {}
        for progress, topic in topic_progress_data:
            # Map topic names to frontend keys
            topic_key = self._map_topic_to_key(topic.name)
            if topic_key:
                learning_progress[topic_key] = int(progress.progress_percentage)

        # Nếu không có dữ liệu tiến độ, tạo mặc định
        if not learning_progress:
            learning_progress = {
                "algorithms": 0,
                "dataStructures": 0,
                "dynamicProgramming": 0,
            }

        # Lấy hoạt động gần đây từ UserActivity
        activities_result = await self.db.execute(
            select(UserActivity)
            .where(UserActivity.user_id == user_id)
            .order_by(UserActivity.created_at.desc())
            .limit(10)
        )
        user_activities = activities_result.scalars().all()

        # Chuyển đổi activities thành format frontend
        activities = []
        for activity in user_activities:
            activity_data = {
                "id": activity.id,
                "name": activity.activity_name,
                "type": activity.activity_type.value,
                "date": activity.created_at.strftime("%d/%m/%Y"),
            }
            if activity.score is not None:
                activity_data["score"] = str(activity.score)
            if activity.progress:
                activity_data["progress"] = activity.progress
            activities.append(activity_data)

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
                    "id": course.id,  # Return as int, not string
                    "name": course.title,
                    "progress": progress,
                    "colorFrom": "blue-500",  # Màu mặc định
                    "colorTo": "indigo-600",  # Màu mặc định
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

    def _map_topic_to_key(self, topic_name: str) -> str:
        """
        Map topic name to frontend key
        """
        topic_mapping = {
            "Thuật toán cơ bản": "algorithms",
            "Algorithms": "algorithms",
            "Cấu trúc dữ liệu": "dataStructures", 
            "Data Structures": "dataStructures",
            "Lập trình động": "dynamicProgramming",
            "Dynamic Programming": "dynamicProgramming",
        }
        return topic_mapping.get(topic_name, "")

    async def add_user_activity(
        self, 
        user_id: int, 
        activity_type: ActivityType, 
        activity_name: str,
        description: str = None,
        score: int = None,
        progress: str = None,
        related_id: int = None
    ) -> UserActivity:
        """
        Thêm hoạt động mới cho người dùng và cập nhật thống kê UserState
        """
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            activity_name=activity_name,
            description=description,
            score=score,
            progress=progress,
            related_id=related_id
        )
        self.db.add(activity)
        
        # Cập nhật UserState thống kê
        await self._update_user_state_stats(user_id, activity_type, score)
        
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def update_topic_progress(
        self,
        user_id: int,
        topic_id: int,
        progress_percentage: float,
        lessons_completed: int = None,
        exercises_completed: int = None
    ) -> UserTopicProgress:
        """
        Cập nhật tiến độ học tập theo chủ đề
        """
        # Tìm hoặc tạo mới UserTopicProgress
        result = await self.db.execute(
            select(UserTopicProgress)
            .where(
                UserTopicProgress.user_id == user_id,
                UserTopicProgress.topic_id == topic_id
            )
        )
        topic_progress = result.scalar_one_or_none()
        
        if not topic_progress:
            # Tạo mới
            topic_progress = UserTopicProgress(
                user_id=user_id,
                topic_id=topic_id,
                progress_percentage=progress_percentage,
                lessons_completed=lessons_completed or 0,
                exercises_completed=exercises_completed or 0
            )
            self.db.add(topic_progress)
        else:
            # Cập nhật
            topic_progress.progress_percentage = progress_percentage
            if lessons_completed is not None:
                topic_progress.lessons_completed = lessons_completed
            if exercises_completed is not None:
                topic_progress.exercises_completed = exercises_completed
            topic_progress.last_activity_at = func.now()
        
        await self.db.commit()
        await self.db.refresh(topic_progress)
        return topic_progress

    async def _update_user_state_stats(self, user_id: int, activity_type: ActivityType, score: int = None) -> None:
        """
        Cập nhật thống kê UserState khi có hoạt động mới
        """
        # Lấy hoặc tạo UserState
        user_state_result = await self.db.execute(
            select(UserState).where(UserState.user_id == user_id)
        )
        user_state = user_state_result.scalar_one_or_none()

        if not user_state:
            user_state = UserState(user_id=user_id)
            self.db.add(user_state)

        # Cập nhật thống kê dựa trên loại hoạt động
        if activity_type == ActivityType.EXERCISE:
            user_state.completed_exercises += 1
            user_state.problems_solved += 1
            if score:
                user_state.total_points += score
            
        elif activity_type == ActivityType.LESSON:
            # Lesson completion gives points
            user_state.total_points += 25
            
        elif activity_type == ActivityType.COURSE:
            user_state.completed_courses += 1
            user_state.total_points += 100
            
        elif activity_type == ActivityType.BADGE:
            user_state.total_points += 50

        # Cập nhật level nếu cần
        await self._update_level(user_state)

    async def _update_level(self, user_state: UserState) -> None:
        """
        Cập nhật level dựa trên tổng điểm
        """
        # Level progression: 100 points per level
        new_level = max(1, user_state.total_points // 100 + 1)
        user_state.level = new_level


def get_profile_service(db: AsyncSession = Depends(get_async_db)) -> ProfileService:
    """
    Dependency để inject ProfileService
    """
    return ProfileService(db)
