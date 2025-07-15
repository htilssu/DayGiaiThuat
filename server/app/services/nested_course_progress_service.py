"""
Service triển khai cách 2: ORM + Response Schema dạng Nested
Query tất cả topics với lessons nested, sau đó map progress status
"""

from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import Depends, HTTPException, status

from app.database.database import get_async_db
from app.models.user_course_model import UserCourse
from app.models.topic_model import Topic
from app.models.user_course_progress_model import UserCourseProgress, ProgressStatus
from app.schemas.nested_course_progress_schema import (
    CourseWithNestedProgressSchema,
    TopicWithProgressSchema,
    LessonWithProgressSchema,
    ProgressMapResponse,
)


class NestedCourseProgressService:
    """
    Service triển khai cách 2: ORM + Response Schema dạng Nested

    Ưu điểm:
    - Query tất cả topics với lessons nested một lần
    - Query progress map riêng biệt
    - Map progress status bằng Python
    - Tránh join phức tạp
    - Performance tốt với khóa học nhỏ/vừa
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_course_with_nested_progress(
        self, user_course_id: int
    ) -> CourseWithNestedProgressSchema:
        """
        Lấy course với topics, lessons và progress nested

        Cách làm:
        1. Query UserCourse để lấy thông tin course
        2. Query tất cả topics với lessons (eager loading)
        3. Query progress map riêng biệt
        4. Map progress status cho từng lesson
        """
        # Step 1: Query UserCourse với course info
        user_course_stmt = (
            select(UserCourse)
            .options(selectinload(UserCourse.course))
            .where(UserCourse.id == user_course_id)
        )

        result = await self.db.execute(user_course_stmt)
        user_course = result.scalar_one_or_none()

        if not user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User course not found"
            )

        # Step 2: Query tất cả topics với lessons nested
        topics_stmt = (
            select(Topic)
            .options(selectinload(Topic.lessons))
            .where(Topic.course_id == user_course.course_id)
            .order_by(Topic.order.asc().nulls_last(), Topic.id)
        )

        topics_result = await self.db.execute(topics_stmt)
        topics = topics_result.scalars().all()

        # Step 3: Query progress map
        progress_map = await self._get_progress_map(user_course_id)

        # Step 4: Build nested response với progress mapping
        nested_topics = []
        total_lessons = 0
        completed_lessons = 0
        in_progress_lessons = 0
        not_started_lessons = 0
        last_activity_at = None
        current_topic_id = None
        current_lesson_id = None

        for topic in topics:
            # Sort lessons by order
            sorted_lessons = sorted(topic.lessons, key=lambda x: (x.order or 0, x.id))

            # Map progress cho từng lesson
            lessons_with_progress = []
            topic_completed = 0

            for lesson in sorted_lessons:
                lesson_progress = progress_map.get(
                    lesson.id,
                    {
                        "status": ProgressStatus.NOT_STARTED,
                        "last_viewed_at": None,
                        "completed_at": None,
                        "completion_percentage": 0.0,
                    },
                )

                # Tính completion percentage
                completion_percentage = {
                    ProgressStatus.NOT_STARTED: 0.0,
                    ProgressStatus.IN_PROGRESS: 50.0,
                    ProgressStatus.COMPLETED: 100.0,
                }.get(lesson_progress["status"], 0.0)

                lesson_with_progress = LessonWithProgressSchema(
                    id=lesson.id,
                    external_id=lesson.external_id,
                    title=lesson.title,
                    description=lesson.description,
                    order=lesson.order,
                    status=lesson_progress["status"],
                    last_viewed_at=lesson_progress["last_viewed_at"],
                    completed_at=lesson_progress["completed_at"],
                    completion_percentage=completion_percentage,
                )

                lessons_with_progress.append(lesson_with_progress)

                # Update counters
                total_lessons += 1
                if lesson_progress["status"] == ProgressStatus.COMPLETED:
                    completed_lessons += 1
                    topic_completed += 1
                elif lesson_progress["status"] == ProgressStatus.IN_PROGRESS:
                    in_progress_lessons += 1
                    # Track current lesson
                    if not current_lesson_id:
                        current_topic_id = topic.id
                        current_lesson_id = lesson.id
                else:
                    not_started_lessons += 1

                # Track last activity
                if lesson_progress["last_viewed_at"]:
                    if (
                        not last_activity_at
                        or lesson_progress["last_viewed_at"] > last_activity_at
                    ):
                        last_activity_at = lesson_progress["last_viewed_at"]

            # Calculate topic completion percentage
            topic_completion_percentage = (
                (topic_completed / len(sorted_lessons)) * 100 if sorted_lessons else 0.0
            )

            topic_with_progress = TopicWithProgressSchema(
                id=topic.id,
                external_id=topic.external_id,
                name=topic.name,
                description=topic.description,
                order=topic.order,
                lessons=lessons_with_progress,
                topic_completion_percentage=topic_completion_percentage,
                completed_lessons=topic_completed,
                total_lessons=len(sorted_lessons),
            )

            nested_topics.append(topic_with_progress)

        # Calculate overall completion percentage
        overall_completion_percentage = (
            (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0.0
        )

        return CourseWithNestedProgressSchema(
            user_course_id=user_course_id,
            course_id=user_course.course_id,
            course_title=user_course.course.title,
            course_description=user_course.course.description,
            topics=nested_topics,
            total_topics=len(nested_topics),
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            in_progress_lessons=in_progress_lessons,
            not_started_lessons=not_started_lessons,
            overall_completion_percentage=round(overall_completion_percentage, 2),
            current_topic_id=current_topic_id,
            current_lesson_id=current_lesson_id,
            last_activity_at=last_activity_at,
        )

    async def _get_progress_map(self, user_course_id: int) -> Dict[int, Dict]:
        """
        Query progress map: lesson_id -> {status, last_viewed_at, completed_at}

        Đây là core của cách 2: Query progress riêng biệt và map bằng Python
        """
        progress_stmt = select(
            UserCourseProgress.lesson_id,
            UserCourseProgress.status,
            UserCourseProgress.last_viewed_at,
            UserCourseProgress.completed_at,
        ).where(UserCourseProgress.user_course_id == user_course_id)

        result = await self.db.execute(progress_stmt)
        progress_records = result.all()

        progress_map = {}
        for record in progress_records:
            # Calculate completion percentage
            completion_percentage = {
                ProgressStatus.NOT_STARTED: 0.0,
                ProgressStatus.IN_PROGRESS: 50.0,
                ProgressStatus.COMPLETED: 100.0,
            }.get(record.status, 0.0)

            progress_map[record.lesson_id] = {
                "status": record.status,
                "last_viewed_at": record.last_viewed_at,
                "completed_at": record.completed_at,
                "completion_percentage": completion_percentage,
            }

        return progress_map

    async def get_progress_map_only(self, user_course_id: int) -> ProgressMapResponse:
        """
        Chỉ lấy progress map mà không cần nested data
        Hữu ích cho frontend muốn tự map hoặc check nhanh
        """
        progress_map = await self._get_progress_map(user_course_id)

        # Calculate summary stats
        total_lessons = len(progress_map)
        completed = sum(
            1 for p in progress_map.values() if p["status"] == ProgressStatus.COMPLETED
        )
        in_progress = sum(
            1
            for p in progress_map.values()
            if p["status"] == ProgressStatus.IN_PROGRESS
        )
        not_started = sum(
            1
            for p in progress_map.values()
            if p["status"] == ProgressStatus.NOT_STARTED
        )

        completion_percentage = (
            (completed / total_lessons * 100) if total_lessons > 0 else 0.0
        )

        summary = {
            "total_lessons": total_lessons,
            "completed_lessons": completed,
            "in_progress_lessons": in_progress,
            "not_started_lessons": not_started,
            "completion_percentage": round(completion_percentage, 2),
        }

        return ProgressMapResponse(
            user_course_id=user_course_id, progress_map=progress_map, summary=summary
        )

    async def get_topic_with_nested_progress(
        self, user_course_id: int, topic_id: int
    ) -> TopicWithProgressSchema:
        """
        Lấy một topic cụ thể với lessons và progress nested
        """
        # Query topic với lessons
        topic_stmt = (
            select(Topic)
            .options(selectinload(Topic.lessons))
            .where(Topic.id == topic_id)
        )

        result = await self.db.execute(topic_stmt)
        topic = result.scalar_one_or_none()

        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )

        # Get progress map
        progress_map = await self._get_progress_map(user_course_id)

        # Build topic with progress
        sorted_lessons = sorted(topic.lessons, key=lambda x: (x.order or 0, x.id))
        lessons_with_progress = []
        topic_completed = 0

        for lesson in sorted_lessons:
            lesson_progress = progress_map.get(
                lesson.id,
                {
                    "status": ProgressStatus.NOT_STARTED,
                    "last_viewed_at": None,
                    "completed_at": None,
                    "completion_percentage": 0.0,
                },
            )

            completion_percentage = {
                ProgressStatus.NOT_STARTED: 0.0,
                ProgressStatus.IN_PROGRESS: 50.0,
                ProgressStatus.COMPLETED: 100.0,
            }.get(lesson_progress["status"], 0.0)

            lesson_with_progress = LessonWithProgressSchema(
                id=lesson.id,
                external_id=lesson.external_id,
                title=lesson.title,
                description=lesson.description,
                order=lesson.order,
                status=lesson_progress["status"],
                last_viewed_at=lesson_progress["last_viewed_at"],
                completed_at=lesson_progress["completed_at"],
                completion_percentage=completion_percentage,
            )

            lessons_with_progress.append(lesson_with_progress)

            if lesson_progress["status"] == ProgressStatus.COMPLETED:
                topic_completed += 1

        # Calculate topic completion percentage
        topic_completion_percentage = (
            (topic_completed / len(sorted_lessons)) * 100 if sorted_lessons else 0.0
        )

        return TopicWithProgressSchema(
            id=topic.id,
            external_id=topic.external_id,
            name=topic.name,
            description=topic.description,
            order=topic.order,
            lessons=lessons_with_progress,
            topic_completion_percentage=round(topic_completion_percentage, 2),
            completed_lessons=topic_completed,
            total_lessons=len(sorted_lessons),
        )


def get_nested_course_progress_service(
    db: AsyncSession = Depends(get_async_db),
) -> NestedCourseProgressService:
    """
    Dependency để inject NestedCourseProgressService
    """
    return NestedCourseProgressService(db)
