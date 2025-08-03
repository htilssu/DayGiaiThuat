from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import Depends, HTTPException, status

from app.database.database import get_async_db
from app.models.user_course_progress_model import UserCourseProgress, ProgressStatus
from app.schemas.user_course_progress_schema import (
    UserCourseProgressCreate,
    UserCourseProgressUpdate,
    UserCourseProgressResponse,
    CourseProgressSummary,
    LessonProgressSummary,
)


class UserCourseProgressService:
    """
    Service để xử lý các thao tác liên quan đến tiến độ học tập của user
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_progress_record(
        self, progress_data: UserCourseProgressCreate
    ) -> UserCourseProgressResponse:
        """
        Tạo một record tiến độ mới cho user trong lesson
        """
        # Kiểm tra xem đã có record cho lesson này chưa
        existing_record = await self.get_progress_by_user_course_and_lesson(
            progress_data.user_course_id,
            progress_data.topic_id,
            progress_data.lesson_id,
        )

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Progress record already exists for this lesson",
            )

        db_progress = UserCourseProgress(**progress_data.model_dump())
        self.db.add(db_progress)
        await self.db.commit()
        await self.db.refresh(db_progress)

        return UserCourseProgressResponse.model_validate(db_progress)

    async def get_progress_by_user_course_and_lesson(
        self, user_course_id: int, topic_id: int, lesson_id: int
    ) -> Optional[UserCourseProgressResponse]:
        """
        Lấy tiến độ của user cho một lesson cụ thể
        """
        stmt = select(UserCourseProgress).where(
            and_(
                UserCourseProgress.user_course_id == user_course_id,
                UserCourseProgress.topic_id == topic_id,
                UserCourseProgress.lesson_id == lesson_id,
            )
        )
        result = await self.db.execute(stmt)
        progress = result.scalar_one_or_none()

        if progress:
            return UserCourseProgressResponse.model_validate(progress)
        return None

    async def update_progress(
        self,
        user_course_id: int,
        topic_id: int,
        lesson_id: int,
        progress_update: UserCourseProgressUpdate,
    ) -> UserCourseProgressResponse:
        """
        Cập nhật tiến độ học tập của user cho một lesson
        """
        # Tìm record hiện tại
        stmt = select(UserCourseProgress).where(
            and_(
                UserCourseProgress.user_course_id == user_course_id,
                UserCourseProgress.topic_id == topic_id,
                UserCourseProgress.lesson_id == lesson_id,
            )
        )
        result = await self.db.execute(stmt)
        progress = result.scalar_one_or_none()

        if not progress:
            # Tạo record mới nếu chưa có
            create_data = UserCourseProgressCreate(
                user_course_id=user_course_id,
                topic_id=topic_id,
                lesson_id=lesson_id,
                status=progress_update.status or ProgressStatus.NOT_STARTED,
            )
            return await self.create_progress_record(create_data)

        # Cập nhật các field được cung cấp
        update_data = progress_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(progress, field, value)

        # Tự động set completed_at khi status = COMPLETED
        if (
            progress_update.status == ProgressStatus.COMPLETED
            and not progress.completed_at
        ):
            progress.completed_at = datetime.utcnow()

        # Reset completed_at nếu status không phải COMPLETED
        if (
            progress_update.status
            and progress_update.status != ProgressStatus.COMPLETED
        ):
            progress.completed_at = None

        progress.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(progress)

        return UserCourseProgressResponse.model_validate(progress)

    async def mark_lesson_viewed(
        self, user_course_id: int, topic_id: int, lesson_id: int
    ) -> UserCourseProgressResponse:
        """
        Đánh dấu lesson đã được xem (chuyển status thành IN_PROGRESS nếu chưa bắt đầu)
        """
        update_data = UserCourseProgressUpdate(
            status=ProgressStatus.IN_PROGRESS, last_viewed_at=datetime.utcnow()
        )

        return await self.update_progress(
            user_course_id, topic_id, lesson_id, update_data
        )

    async def mark_lesson_completed(
        self, user_course_id: int, topic_id: int, lesson_id: int
    ) -> UserCourseProgressResponse:
        """
        Đánh dấu lesson đã hoàn thành
        """
        update_data = UserCourseProgressUpdate(
            status=ProgressStatus.COMPLETED,
            completed_at=datetime.utcnow(),
            last_viewed_at=datetime.utcnow(),
        )

        return await self.update_progress(
            user_course_id, topic_id, lesson_id, update_data
        )

    async def get_user_course_progress_summary(
        self, user_course_id: int
    ) -> CourseProgressSummary:
        """
        Lấy tóm tắt tiến độ học tập cho một khóa học
        """
        # Đếm số lesson theo status
        stmt = select(
            func.count().label("total"),
            func.count()
            .filter(UserCourseProgress.status == ProgressStatus.COMPLETED)
            .label("completed"),
            func.count()
            .filter(UserCourseProgress.status == ProgressStatus.IN_PROGRESS)
            .label("in_progress"),
            func.count()
            .filter(UserCourseProgress.status == ProgressStatus.NOT_STARTED)
            .label("not_started"),
            func.max(UserCourseProgress.last_viewed_at).label("last_activity"),
        ).where(UserCourseProgress.user_course_id == user_course_id)

        result = await self.db.execute(stmt)
        stats = result.first()

        if not stats or stats.total == 0:
            return CourseProgressSummary(
                user_course_id=user_course_id,
                total_lessons=0,
                completed_lessons=0,
                in_progress_lessons=0,
                not_started_lessons=0,
                completion_percentage=0.0,
                current_topic_id=None,
                current_lesson_id=None,
                last_activity_at=None,
            )

        # Tìm lesson hiện tại (lesson IN_PROGRESS gần nhất hoặc lesson COMPLETED gần nhất)
        current_lesson_stmt = (
            select(UserCourseProgress.topic_id, UserCourseProgress.lesson_id)
            .where(
                and_(
                    UserCourseProgress.user_course_id == user_course_id,
                    UserCourseProgress.status.in_(
                        [ProgressStatus.IN_PROGRESS, ProgressStatus.COMPLETED]
                    ),
                )
            )
            .order_by(UserCourseProgress.last_viewed_at.desc())
            .limit(1)
        )

        current_result = await self.db.execute(current_lesson_stmt)
        current_lesson = current_result.first()

        completion_percentage = (
            (stats.completed / stats.total) * 100 if stats.total > 0 else 0
        )

        return CourseProgressSummary(
            user_course_id=user_course_id,
            total_lessons=stats.total,
            completed_lessons=stats.completed or 0,
            in_progress_lessons=stats.in_progress or 0,
            not_started_lessons=stats.not_started or 0,
            completion_percentage=round(completion_percentage, 2),
            current_topic_id=current_lesson.topic_id if current_lesson else None,
            current_lesson_id=current_lesson.lesson_id if current_lesson else None,
            last_activity_at=stats.last_activity,
        )

    async def get_lessons_progress_by_topic(
        self, user_course_id: int, topic_id: int
    ) -> List[LessonProgressSummary]:
        """
        Lấy tiến độ của tất cả lesson trong một topic
        """
        stmt = (
            select(UserCourseProgress)
            .where(
                and_(
                    UserCourseProgress.user_course_id == user_course_id,
                    UserCourseProgress.topic_id == topic_id,
                )
            )
            .order_by(UserCourseProgress.lesson_id)
        )

        result = await self.db.execute(stmt)
        progress_records = result.scalars().all()

        summaries = []
        for record in progress_records:
            # Tính phần trăm hoàn thành đơn giản (0%, 50%, 100%)
            completion_percentage = {
                ProgressStatus.NOT_STARTED: 0.0,
                ProgressStatus.IN_PROGRESS: 50.0,
                ProgressStatus.COMPLETED: 100.0,
            }.get(record.status, 0.0)

            summaries.append(
                LessonProgressSummary(
                    topic_id=record.topic_id,
                    lesson_id=record.lesson_id,
                    status=record.status,
                    completion_percentage=completion_percentage,
                    last_viewed_at=record.last_viewed_at,
                )
            )

        return summaries

    async def get_user_progress_by_course(
        self, user_course_id: int
    ) -> List[UserCourseProgressResponse]:
        """
        Lấy tất cả progress records của user cho một khóa học
        """
        stmt = (
            select(UserCourseProgress)
            .where(UserCourseProgress.user_course_id == user_course_id)
            .order_by(UserCourseProgress.topic_id, UserCourseProgress.lesson_id)
        )

        result = await self.db.execute(stmt)
        progress_records = result.scalars().all()

        return [
            UserCourseProgressResponse.model_validate(record)
            for record in progress_records
        ]

    async def delete_progress_record(
        self, user_course_id: int, topic_id: int, lesson_id: int
    ) -> bool:
        """
        Xóa một progress record
        """
        stmt = select(UserCourseProgress).where(
            and_(
                UserCourseProgress.user_course_id == user_course_id,
                UserCourseProgress.topic_id == topic_id,
                UserCourseProgress.lesson_id == lesson_id,
            )
        )
        result = await self.db.execute(stmt)
        progress = result.scalar_one_or_none()

        if not progress:
            return False

        await self.db.delete(progress)
        await self.db.commit()
        return True


def get_user_course_progress_service(
    db: AsyncSession = Depends(get_async_db),
) -> UserCourseProgressService:
    """
    Dependency để inject UserCourseProgressService
    """
    return UserCourseProgressService(db)
