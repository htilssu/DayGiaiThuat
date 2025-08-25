from typing import Optional

from fastapi import HTTPException, status, Depends
from google.api_core.retry import if_exception_type
from sqlalchemy import and_, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import (
    get_async_db,
    AsyncSessionLocal,
    get_independent_db_session,
)
from app.models import Lesson
from app.models.course_model import Course
from app.models.topic_model import Topic
from app.models.user_course_model import UserCourse
from app.models.user_course_progress_model import UserCourseProgress, ProgressStatus
from app.schemas.course_draft_schema import CourseDraftSchema
from app.schemas.course_schema import (
    BulkDeleteCoursesResponse,
    CourseCreate,
    CourseDetailResponse,
    CourseDetailWithProgressResponse,
    TopicWithProgressResponse,
    UserCourseListItem,
    CourseBaseUser,
)
from app.schemas.lesson_schema import (
    LessonWithProgressResponse,
)


class CourseService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_courses(self, skip: int = 0, limit: int = 10):

        result = await self.db.execute(
            select(Course)
            .filter(Course.is_published == True)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_course(self, course_id: int, user_id: int | None = None):

        result = await self.db.execute(
            select(Course)
            .options(selectinload(Course.topics))
            .filter(Course.id == course_id)
        )
        course = result.scalar_one_or_none()
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )

        return course

    async def create_course(self, course_data: CourseCreate):

        try:
            new_course = Course(**course_data.model_dump())

            self.db.add(new_course)
            await self.db.commit()
            await self.db.refresh(new_course)

            result = await self.db.execute(
                select(Course)
                .options(selectinload(Course.topics))
                .filter(Course.id == new_course.id)
            )
            course_with_topics = result.scalar_one()

            return course_with_topics
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi tạo khóa học: {str(e)}",
            )

    async def update_course(self, course_id: int, course_data):
        try:
            result = await self.db.execute(
                select(Course).filter(Course.id == course_id)
            )
            course = result.scalars().first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            course_dict = course_data.dict(exclude_unset=True)
            for key, value in course_dict.items():
                setattr(course, key, value)

            await self.db.commit()
            await self.db.refresh(course)

            return course
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi cập nhật khóa học: {str(e)}",
            )

    async def delete_course(self, course_id: int):

        try:
            # Tìm khóa học cần xóa
            result = await self.db.execute(
                select(Course).filter(Course.id == course_id)
            )
            course = result.scalars().first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Xóa khóa học
            await self.db.delete(course)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi xóa khóa học: {str(e)}",
            )

    async def bulk_delete_courses(self, course_ids: list[int]):
        from app.models.topic_model import Topic
        from app.models.lesson_model import Lesson, LessonSection

        deleted_courses = []
        failed_courses = []
        errors = []
        deleted_items = {"courses": 0, "topics": 0, "lessons": 0, "lesson_sections": 0}

        for course_id in course_ids:
            try:
                result = await self.db.execute(
                    select(Course).filter(Course.id == course_id)
                )
                course = result.scalars().first()
                if not course:
                    failed_courses.append(course_id)
                    errors.append(f"Không tìm thấy khóa học với ID {course_id}")
                    continue

                result = await self.db.execute(
                    select(func.count())
                    .select_from(UserCourse)
                    .where(UserCourse.course_id == course_id)
                )
                enrollment_count = result.scalar_one()

                if enrollment_count > 0:
                    failed_courses.append(course_id)
                    errors.append(
                        f"Khóa học {course_id} đang có {enrollment_count} học viên đăng ký, không thể xóa"
                    )
                    continue

                # Đếm số lượng items sẽ bị xóa để logging
                topics_count_result = await self.db.execute(
                    select(func.count())
                    .select_from(Topic)
                    .where(Topic.course_id == course_id)
                )
                topics_count = topics_count_result.scalar_one()

                lessons_count_result = await self.db.execute(
                    select(func.count())
                    .select_from(Lesson)
                    .join(Topic, Lesson.topic_id == Topic.id)
                    .where(Topic.course_id == course_id)
                )
                lessons_count = lessons_count_result.scalar_one()
                sections_count_result = await self.db.execute(
                    select(func.count())
                    .select_from(LessonSection)
                    .join(Lesson, LessonSection.lesson_id == Lesson.id)
                    .join(Topic, Lesson.topic_id == Topic.id)
                    .where(Topic.course_id == course_id)
                )
                sections_count = sections_count_result.scalar_one()

                # Xóa khóa học (cascade sẽ tự động xóa topics, lessons, sections)
                await self.db.delete(course)
                deleted_courses.append(course_id)

                # Cập nhật thống kê
                deleted_items["courses"] += 1
                deleted_items["topics"] += topics_count
                deleted_items["lessons"] += lessons_count
                deleted_items["lesson_sections"] += sections_count

            except SQLAlchemyError as e:
                failed_courses.append(course_id)
                errors.append(f"Lỗi khi xóa khóa học {course_id}: {str(e)}")
                continue
            except Exception as e:
                failed_courses.append(course_id)
                errors.append(
                    f"Lỗi không xác định khi xóa khóa học {course_id}: {str(e)}"
                )
                continue

        try:
            # Commit tất cả các thay đổi
            if deleted_courses:
                await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            # Nếu commit thất bại, tất cả courses đều failed
            failed_courses.extend(deleted_courses)
            deleted_courses = []
            deleted_items = {
                "courses": 0,
                "topics": 0,
                "lessons": 0,
                "lesson_sections": 0,
            }
            errors.append(f"Lỗi khi commit transaction: {str(e)}")

        return BulkDeleteCoursesResponse(
            deleted_count=len(deleted_courses),
            failed_count=len(failed_courses),
            deleted_courses=deleted_courses,
            failed_courses=failed_courses,
            errors=errors,
            deleted_items=deleted_items,
        )

    async def enroll_course(self, user_id: int, course_id: int):

        try:

            result = await self.db.execute(
                select(Course).filter(Course.id == course_id)
            )
            course = result.scalar_one_or_none()
            if not course:
                raise HTTPException(
                    status_code=404,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Kiểm tra xem người dùng đã đăng ký khóa học này chưa
            existing_enrollment = await self.db.execute(
                select(UserCourse).filter(
                    and_(
                        UserCourse.user_id == user_id, UserCourse.course_id == course_id
                    )
                )
            )
            existing_enrollment = existing_enrollment.scalar_one_or_none()

            if existing_enrollment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Người dùng đã đăng ký khóa học này",
                )

            enrollment = UserCourse(user_id=user_id, course_id=course_id)
            self.db.add(enrollment)
            await self.db.commit()
            await self.db.refresh(enrollment)

            from app.models.test_model import Test

            entry_test = await self.db.execute(
                select(Test).filter(Test.course_id == course_id)
            )
            entry_test = entry_test.scalar_one_or_none()

            result = {
                "enrollment": enrollment,
                "has_entry_test": entry_test is not None,
                "entry_test_id": entry_test.id if entry_test else None,
            }

            return result
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi khi đăng ký khóa học: {str(e)}",
            )

    async def get_user_courses(self, user_id: int) -> list[UserCourseListItem]:

        enrollments = await self.db.execute(
            select(UserCourse).filter(UserCourse.user_id == user_id)
        )
        enrollments = enrollments.scalars().all()
        course_ids = [enrollment.course_id for enrollment in enrollments]

        courses = await self.db.execute(
            select(Course)
            .options(selectinload(Course.topics).selectinload(Topic.lessons))
            .filter(Course.id.in_(course_ids))
        )
        courses = courses.scalars().all()

        result = []
        for course in courses:
            user_course = next(
                (e for e in enrollments if e.course_id == course.id), None
            )
            user_course_id = user_course.id if user_course else None

            total_lessons = 0
            for topic in course.topics:
                total_lessons += len(topic.lessons)

            completed_lessons = 0
            if user_course_id:
                progress_records = await self.db.execute(
                    select(func.count(UserCourseProgress.id)).filter(
                        UserCourseProgress.user_course_id == user_course_id,
                        UserCourseProgress.status == ProgressStatus.COMPLETED,
                    )
                )
                completed_lessons = progress_records.scalar() or 0

            progress = (
                (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
            )

            current_topic_id = None
            current_lesson_id = None

            if user_course_id and total_lessons > 0:
                completed_lesson_records = await self.db.execute(
                    select(UserCourseProgress.lesson_id).filter(
                        UserCourseProgress.user_course_id == user_course_id,
                        UserCourseProgress.status == ProgressStatus.COMPLETED,
                    )
                )
                completed_lesson_ids = set(completed_lesson_records.scalars().all())

                found_current = False
                for topic in sorted(course.topics, key=lambda t: t.order):
                    if found_current:
                        break
                    for lesson in sorted(
                        topic.lessons, key=lambda lesson: lesson.order
                    ):
                        if lesson.id not in completed_lesson_ids:
                            current_topic_id = topic.id
                            current_lesson_id = lesson.id
                            found_current = True
                            break

                if not found_current and course.topics:
                    last_topic = max(course.topics, key=lambda t: t.order)
                    if last_topic.lessons:
                        last_lesson = max(
                            last_topic.lessons, key=lambda lesson: lesson.order
                        )
                        current_topic_id = last_topic.id
                        current_lesson_id = last_lesson.id

            result.append(
                UserCourseListItem(
                    id=course.id,
                    title=course.title,
                    description=course.description,
                    thumbnail_url=course.thumbnail_url,
                    level=course.level,
                    duration=course.duration,
                    price=course.price,
                    is_published=course.is_published,
                    tags=course.tags,
                    requirements=course.requirements,
                    what_you_will_learn=course.what_you_will_learn,
                    created_at=course.created_at,
                    updated_at=course.updated_at,
                    test_generation_status=course.test_generation_status,
                    progress=round(progress, 2),
                    current_topic_id=current_topic_id,
                    current_lesson_id=current_lesson_id,
                )
            )

        return result

    async def get_topics(self, course_id):
        result = await self.db.execute(
            select(Topic)
            .options(selectinload(Topic.lessons).selectinload(Lesson.progress_records))
            .order_by(Topic.order)
            .filter(Topic.course_id == course_id)
        )
        topics = result.scalars().all()
        return topics


def is_enrolled(self, user_id: int, course_id: int):
    enrollment = self.db.execute(
        select(UserCourse).filter(
            UserCourse.user_id == user_id, UserCourse.course_id == course_id
        )
    )
    return enrollment is not None


async def update_course_thumbnail(self, course_id: int, thumbnail_url: str):
    try:
        await self.db.execute(
            text(
                "UPDATE courses SET thumbnail_url = :thumbnail_url WHERE id = :course_id"
            ),
            {"thumbnail_url": thumbnail_url, "course_id": course_id},
        )
        await self.db.commit()

        result = await self.db.execute(
            select(Course)
            .options(selectinload(Course.topics))
            .filter(Course.id == course_id)
        )
        updated_course = result.scalar_one_or_none()
        if not updated_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )
        return updated_course
    except SQLAlchemyError as e:
        await self.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật ảnh thumbnail: {str(e)}",
        )


async def get_course_entry_test(self, course_id: int):
    try:
        course = await self.db.execute(select(Course).filter(Course.id == course_id))
        course = course.scalar_one_or_none()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )

        # Lấy test đầu vào
        from app.models.test_model import Test

        entry_test = await self.db.execute(
            select(Test).filter(Test.course_id == course_id)
        )
        entry_test = entry_test.scalar_one_or_none()

        return entry_test
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy test đầu vào: {str(e)}",
        )


async def get_course_with_progress(
    course_id: int, user_id: Optional[int] = None
) -> CourseBaseUser:
    async with get_independent_db_session() as db:
        user_course = (
            await db.execute(
                select(UserCourse)
                .filter(UserCourse.user_id == user_id)
                .options(selectinload(UserCourse.course).selectinload(Course.topics))
            )
        ).scalar_one_or_none()
        if user_course:
            course = user_course.course
        else:
            course = await db.execute(
                select(Course)
                .options(selectinload(Course.topics))
                .filter(Course.id == course_id)
            )
            course = course.scalar_one_or_none()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        response = CourseBaseUser.model_validate(course)
        response.status = user_course.status if user_course else None
        return response


async def save_course_from_draft(draft: CourseDraftSchema):
    async with AsyncSessionLocal() as db:
        query_result = db.execute(select(Course).filter(Course.id == draft.course_id))
        course = query_result.scalar_one_or_none()

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {draft.course_id}",
            )

        course.duration = draft.duration
        course.description = draft.description

        await db.commit()


def get_course_service(db: AsyncSession = Depends(get_async_db)):
    return CourseService(db)
