from fastapi import HTTPException, status, Depends
from sqlalchemy import and_, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_async_db

from app.models.user_course_model import UserCourse
from app.models.user_course_progress_model import UserCourseProgress, ProgressStatus
from app.models.topic_model import Topic
from app.models.course_model import Course
from app.schemas.course_schema import (
    BulkDeleteCoursesResponse,
    CourseCreate,
    CourseDetailResponse,
    CourseDetailWithProgressResponse,
    TopicWithProgressResponse,
    UserCourseListItem,
)
from app.schemas.lesson_schema import (
    LessonWithChildSchema,
    LessonSectionSchema,
    LessonWithProgressResponse,
)
from app.schemas.topic_schema import TopicResponse
from typing import Optional


class CourseService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_courses(self, skip: int = 0, limit: int = 10):
        """
        Lấy danh sách khóa học với phân trang

        Args:
            skip: Số lượng bản ghi bỏ qua
            limit: Số lượng bản ghi tối đa trả về

        Returns:
            List[Course]: Danh sách khóa học
        """
        result = await self.db.execute(
            select(Course)
            .filter(Course.is_published == True)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_course(self, course_id: int, user_id: int | None = None):
        """
        Lấy thông tin chi tiết của một khóa học

        Args:
            course_id: ID của khóa học

        Returns:
            Course: Thông tin chi tiết của khóa học
        """
        result = await self.db.execute(
            select(Course)
            .options(selectinload(Course.topics).selectinload(Topic.lessons))
            .filter(Course.id == course_id)
        )
        course = result.scalar_one_or_none()
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )
        list_topic_response = []

        for topic in course.topics:
            is_completed = False
            progress = 0
            completed_lessons = 0

            topic_response = TopicResponse(
                id=topic.id,
                lessons=[
                    LessonWithChildSchema(
                        id=lesson.id,
                        title=lesson.title,
                        description=lesson.description,
                        order=lesson.order,
                        external_id=lesson.external_id,
                        sections=[
                            LessonSectionSchema(
                                type=section.type,
                                content=section.content,
                                order=section.order,
                                options=section.options,
                                answer=section.answer,
                                explanation=section.explanation,
                            )
                            for section in lesson.sections
                        ],
                        exercises=[],
                        is_completed=False,
                        next_lesson_id=None,
                        prev_lesson_id=None,
                    )
                    for lesson in topic.lessons
                ],
                name=topic.name,
                description=topic.description,
                prerequisites=topic.prerequisites,
                order=topic.order,
                created_at=topic.created_at,
                updated_at=topic.updated_at,
                external_id=topic.external_id,
                course_id=topic.course_id,
                is_completed=is_completed,
                progress=progress,
                completed_lessons=completed_lessons,
            )
            list_topic_response.append(topic_response)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )
        is_enrolled = False

        if user_id is not None:
            result = await self.db.execute(
                select(UserCourse).filter(
                    and_(
                        UserCourse.user_id == user_id,
                        UserCourse.course_id == course_id,
                    )
                )
            )
            user_course = result.scalar_one_or_none()
            if user_course is not None:
                is_enrolled = True

        return CourseDetailResponse(
            description=course.description,
            thumbnail_url=course.thumbnail_url,
            id=course.id,
            created_at=course.created_at,
            updated_at=course.updated_at,
            test_generation_status=course.test_generation_status,
            is_enrolled=is_enrolled,
            title=course.title,
            level=course.level,
            topics=list_topic_response,
            duration=course.duration,
            price=course.price,
            is_published=course.is_published,
            tags=course.tags,
            requirements=course.requirements,
            what_you_will_learn=course.what_you_will_learn,
        )

    async def create_course(self, course_data: CourseCreate):
        """
        Tạo một khóa học mới

        Args:
            course_data: Dữ liệu để tạo khóa học

        Returns:
            Course: Thông tin của khóa học vừa tạo
        """
        try:
            # Tạo đối tượng Course từ dữ liệu đầu vào
            new_course = Course(**course_data.model_dump())

            # Thêm vào database
            self.db.add(new_course)
            await self.db.commit()
            await self.db.refresh(new_course)

            # Tải lại course với topics để tránh lỗi lazy loading
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
        """
        Cập nhật thông tin một khóa học

        Args:
            course_id: ID của khóa học cần cập nhật
            course_data: Dữ liệu cập nhật

        Returns:
            Course: Thông tin khóa học sau khi cập nhật
        """
        try:
            # Tìm khóa học cần cập nhật
            result = await self.db.execute(
                select(Course).filter(Course.id == course_id)
            )
            course = result.scalars().first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Cập nhật thông tin khóa học từ dữ liệu đầu vào
            course_dict = course_data.dict(exclude_unset=True)
            for key, value in course_dict.items():
                setattr(course, key, value)

            # Lưu thay đổi vào database
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
        """
        Xóa một khóa học

        Args:
            course_id: ID của khóa học cần xóa

        Returns:
            bool: True nếu xóa thành công
        """
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
        """
        Xóa nhiều khóa học cùng lúc, bao gồm tất cả topics, lessons, và lesson sections

        Args:
            course_ids: Danh sách ID các khóa học cần xóa

        Returns:
            dict: Thông tin về quá trình xóa bao gồm:
                - deleted_count: Số lượng khóa học đã xóa thành công
                - failed_count: Số lượng khóa học không thể xóa
                - deleted_courses: Danh sách ID các khóa học đã xóa
                - failed_courses: Danh sách ID các khóa học không thể xóa
                - errors: Danh sách lỗi chi tiết
                - deleted_items: Thống kê chi tiết số lượng items đã xóa
        """
        from app.models.topic_model import Topic
        from app.models.lesson_model import Lesson, LessonSection

        deleted_courses = []
        failed_courses = []
        errors = []
        deleted_items = {"courses": 0, "topics": 0, "lessons": 0, "lesson_sections": 0}

        for course_id in course_ids:
            try:
                # Tìm khóa học cần xóa
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
        """
        Đăng ký khóa học cho người dùng

        Args:
            user_id: ID của người dùng
            course_id: ID của khóa học

        Returns:
            dict: Thông tin đăng ký khóa học và test đầu vào (nếu có)
        """
        try:

            # Kiểm tra xem khóa học có tồn tại không
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

            # Tạo đăng ký mới
            enrollment = UserCourse(user_id=user_id, course_id=course_id)
            self.db.add(enrollment)
            await self.db.commit()
            await self.db.refresh(enrollment)

            # Kiểm tra xem có test đầu vào cho khóa học này không
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
        """
        Lấy danh sách khóa học mà người dùng đã đăng ký, kèm progress

        Args:
            user_id: ID của người dùng

        Returns:
            List[UserCourseListItem]: Danh sách khóa học với trường progress
        """
        try:

            # Lấy danh sách khóa học mà người dùng đã đăng ký
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

            # Tính progress cho từng khóa học
            result = []
            for course in courses:
                # Lấy user_course_id
                user_course = next(
                    (e for e in enrollments if e.course_id == course.id), None
                )
                user_course_id = user_course.id if user_course else None

                # Đếm tổng số bài học
                total_lessons = 0
                for topic in course.topics:
                    total_lessons += len(topic.lessons)

                # Đếm số bài đã hoàn thành bằng một query duy nhất
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
                    (completed_lessons / total_lessons * 100)
                    if total_lessons > 0
                    else 0.0
                )

                # Tìm bài học hiện tại (bài học đầu tiên chưa hoàn thành)
                current_topic_id = None
                current_lesson_id = None

                if user_course_id and total_lessons > 0:
                    # Tìm tất cả các bài học đã hoàn thành
                    completed_lesson_records = await self.db.execute(
                        select(UserCourseProgress.lesson_id).filter(
                            UserCourseProgress.user_course_id == user_course_id,
                            UserCourseProgress.status == ProgressStatus.COMPLETED,
                        )
                    )
                    completed_lesson_ids = set(completed_lesson_records.scalars().all())

                    # Tìm bài học đầu tiên chưa hoàn thành
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

                    # Nếu tất cả bài học đã hoàn thành, lấy bài học cuối cùng
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
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi khi lấy danh sách khóa học: {str(e)}",
            )

    def is_enrolled(self, user_id: int, course_id: int):
        """
        Kiểm tra xem người dùng đã đăng ký khóa học chưa

        Args:
            user_id: ID của người dùng
            course_id: ID của khóa học

        Returns:
            bool: True nếu người dùng đã đăng ký khóa học
        """
        enrollment = self.db.execute(
            select(UserCourse).filter(
                UserCourse.user_id == user_id, UserCourse.course_id == course_id
            )
        )
        return enrollment is not None

    async def update_course_thumbnail(self, course_id: int, thumbnail_url: str):
        """
        Cập nhật ảnh thumbnail cho khóa học

        Args:
            course_id (int): ID của khóa học
            thumbnail_url (str): URL của ảnh thumbnail mới

        Returns:
            Course: Thông tin khóa học sau khi cập nhật

        Raises:
            HTTPException: Nếu không tìm thấy khóa học hoặc có lỗi database
        """
        try:
            await self.db.execute(
                text(
                    "UPDATE courses SET thumbnail_url = :thumbnail_url WHERE id = :course_id"
                ),
                {"thumbnail_url": thumbnail_url, "course_id": course_id},
            )
            await self.db.commit()

            # Fetch and return the updated course with topics
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
        """
        Lấy test đầu vào của khóa học

        Args:
            course_id: ID của khóa học

        Returns:
            Test: Test đầu vào của khóa học (nếu có)

        Raises:
            HTTPException: Nếu không tìm thấy khóa học
        """
        try:
            # Kiểm tra khóa học có tồn tại không
            course = await self.db.execute(
                select(Course).filter(Course.id == course_id)
            )
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

    # Methods with Progress Support
    async def get_course_with_progress(
        self, course_id: int, user_id: Optional[int] = None
    ) -> CourseDetailWithProgressResponse:
        """Lấy course với nested progress data"""
        # Get course with topics and lessons
        course = await self.db.execute(
            select(Course)
            .options(selectinload(Course.topics).selectinload(Topic.lessons))
            .filter(Course.id == course_id)
        )
        course = course.scalar_one_or_none()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check enrollment
        user_course_id = None
        is_enrolled = False
        if user_id:
            user_course = await self.db.execute(
                select(UserCourse).filter(
                    UserCourse.user_id == user_id, UserCourse.course_id == course_id
                )
            )
            user_course = user_course.scalar_one_or_none()
            if user_course:
                is_enrolled = True
                user_course_id = user_course.id

        # Get progress map
        progress_map = {}
        if user_course_id:
            progress_records = await self.db.execute(
                select(UserCourseProgress).filter(
                    UserCourseProgress.user_course_id == user_course_id
                )
            )
            progress_map = {
                (p.topic_id, p.lesson_id): p for p in progress_records.scalars()
            }

        # Build topics with progress
        topics = []
        total_lessons = 0
        completed_lessons = 0
        in_progress_lessons = 0
        not_started_lessons = 0
        current_topic_id = None
        current_lesson_id = None
        last_activity_at = None

        for topic in sorted(course.topics, key=lambda x: x.order or 0):
            # Build lessons for this topic
            lessons = []
            topic_completed = 0
            topic_total = len(topic.lessons)

            for lesson in sorted(topic.lessons, key=lambda x: x.order):
                progress_key = (topic.id, lesson.id)
                progress = progress_map.get(progress_key)

                lesson_status = ProgressStatus.NOT_STARTED
                lesson_last_viewed = None
                lesson_completed_at = None
                lesson_completion = 0.0

                if progress:
                    lesson_status = progress.status
                    lesson_last_viewed = progress.updated_at
                    lesson_completed_at = (
                        progress.completed_at
                        if progress.status == ProgressStatus.COMPLETED
                        else None
                    )
                    lesson_completion = (
                        100.0
                        if progress.status == ProgressStatus.COMPLETED
                        else (
                            50.0
                            if progress.status == ProgressStatus.IN_PROGRESS
                            else 0.0
                        )
                    )

                    # Track current position and last activity
                    if progress.status == ProgressStatus.IN_PROGRESS:
                        current_topic_id = topic.id
                        current_lesson_id = lesson.id

                    if not last_activity_at or (
                        progress.updated_at and progress.updated_at > last_activity_at
                    ):
                        last_activity_at = progress.updated_at

                # Count lesson status
                if lesson_status == ProgressStatus.COMPLETED:
                    completed_lessons += 1
                    topic_completed += 1
                elif lesson_status == ProgressStatus.IN_PROGRESS:
                    in_progress_lessons += 1
                else:
                    not_started_lessons += 1

                total_lessons += 1

                lessons.append(
                    LessonWithProgressResponse(
                        id=lesson.id,
                        external_id=lesson.external_id,
                        title=lesson.title,
                        description=lesson.description,
                        order=lesson.order,
                        next_lesson_id=None,
                        prev_lesson_id=None,
                        sections=[],
                        exercises=[],
                        is_completed=lesson_status == ProgressStatus.COMPLETED,
                        status=lesson_status,
                        last_viewed_at=lesson_last_viewed,
                        completed_at=lesson_completed_at,
                        completion_percentage=lesson_completion,
                    )
                )

            # Calculate topic completion percentage
            topic_completion_percentage = (
                (topic_completed / topic_total * 100) if topic_total > 0 else 0.0
            )

            topics.append(
                TopicWithProgressResponse(
                    id=topic.id,
                    external_id=topic.external_id,
                    name=topic.name,
                    description=topic.description,
                    order=topic.order,
                    lessons=lessons,
                    topic_completion_percentage=round(topic_completion_percentage, 2),
                    completed_lessons=topic_completed,
                    total_lessons=topic_total,
                )
            )

        # Calculate overall completion percentage
        overall_completion_percentage = (
            (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
        )

        # Get current lesson details if exists
        current_lesson = None
        if current_lesson_id:
            for topic in course.topics:
                for lesson in topic.lessons:
                    if lesson.id == current_lesson_id:
                        current_lesson = {
                            "id": lesson.id,
                            "external_id": lesson.external_id,
                            "title": lesson.title,
                            "description": lesson.description,
                            "order": lesson.order,
                            "topic_id": topic.id,
                        }
                        break
                if current_lesson:
                    break

        # Build final response
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "thumbnail_url": course.thumbnail_url,
            "level": course.level,
            "duration": course.duration,
            "price": course.price,
            "is_published": course.is_published,
            "tags": course.tags,
            "requirements": course.requirements,
            "what_you_will_learn": course.what_you_will_learn,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "test_generation_status": course.test_generation_status,
            "is_enrolled": is_enrolled,
            "topics": topics,
            "user_course_id": user_course_id,
            "overall_completion_percentage": round(overall_completion_percentage, 2),
            "total_topics": len(topics),
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "in_progress_lessons": in_progress_lessons,
            "not_started_lessons": not_started_lessons,
            "current_topic_id": current_topic_id,
            "current_lesson_id": current_lesson_id,
            "current_lesson": current_lesson,
            "last_activity_at": last_activity_at,
        }

        return CourseDetailWithProgressResponse(**course_dict)


def get_course_service(db: AsyncSession = Depends(get_async_db)):
    """
    Factory function to get CourseService instance with database session and optional test generation service
    Note: Do NOT use Session as a response_model or return type in FastAPI routes. Only use Pydantic schemas or serializable types.
    """
    return CourseService(db)
