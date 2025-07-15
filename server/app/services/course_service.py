from fastapi import HTTPException, status
from sqlalchemy import and_, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.user_course_model import UserCourse
from app.models.user_course_progress_model import UserCourseProgress, ProgressStatus
from app.models.topic_model import Topic
from app.models.lesson_model import Lesson
from app.models.user_model import User
from app.models.course_model import Course
from app.schemas.course_schema import (
    CourseCreate,
    CourseDetailResponse,
    CourseDetailWithProgressResponse,
    TopicDetailWithProgressResponse,
    LessonDetailWithProgressResponse,
    LessonWithProgressResponse,
    TopicWithProgressResponse,
)
from app.schemas.lesson_schema import LessonResponseSchema, LessonSectionSchema
from app.schemas.topic_schema import TopicResponse
from typing import Optional


class CourseService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_courses(self, skip: int = 0, limit: int = 10):
        """
        Lấy danh sách khóa học với phân trang

        Args:
            skip: Số lượng bản ghi bỏ qua
            limit: Số lượng bản ghi tối đa trả về

        Returns:
            List[Course]: Danh sách khóa học
        """
        return self.db.query(Course).offset(skip).limit(limit).all()

    def get_course(self, course_id: int, user_id: int | None = None):
        """
        Lấy thông tin chi tiết của một khóa học

        Args:
            course_id: ID của khóa học

        Returns:
            Course: Thông tin chi tiết của khóa học
        """
        course = self.db.query(Course).filter(Course.id == course_id).first()
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
                    LessonResponseSchema(
                        id=lesson.id,
                        title=lesson.title,
                        description=lesson.description,
                        order=lesson.order,
                        external_id=lesson.external_id,
                        topic_id=lesson.topic_id,
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
            user_course = (
                self.db.query(UserCourse)
                .where(UserCourse.user_id == user_id, UserCourse.course_id == course_id)
                .first()
            )
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

    def create_course(self, course_data: CourseCreate):
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
            self.db.commit()
            self.db.refresh(new_course)

            return new_course
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi tạo khóa học: {str(e)}",
            )

    def update_course(self, course_id: int, course_data):
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
            course = self.db.query(Course).filter(Course.id == course_id).first()
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
            self.db.commit()
            self.db.refresh(course)

            return course
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi cập nhật khóa học: {str(e)}",
            )

    def delete_course(self, course_id: int):
        """
        Xóa một khóa học

        Args:
            course_id: ID của khóa học cần xóa

        Returns:
            bool: True nếu xóa thành công
        """
        try:
            # Tìm khóa học cần xóa
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Xóa khóa học
            self.db.delete(course)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi xóa khóa học: {str(e)}",
            )

    def bulk_delete_courses(self, course_ids: list[int]):
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
                course = self.db.query(Course).filter(Course.id == course_id).first()
                if not course:
                    failed_courses.append(course_id)
                    errors.append(f"Không tìm thấy khóa học với ID {course_id}")
                    continue

                # Kiểm tra xem khóa học có đang được sử dụng không
                enrollment_count = (
                    self.db.query(UserCourse)
                    .filter(UserCourse.course_id == course_id)
                    .count()
                )

                if enrollment_count > 0:
                    failed_courses.append(course_id)
                    errors.append(
                        f"Khóa học {course_id} đang có {enrollment_count} học viên đăng ký, không thể xóa"
                    )
                    continue

                # Đếm số lượng items sẽ bị xóa để logging
                topics_count = (
                    self.db.query(Topic).filter(Topic.course_id == course_id).count()
                )
                lessons_count = (
                    self.db.query(Lesson)
                    .join(Topic)
                    .filter(Topic.course_id == course_id)
                    .count()
                )
                sections_count = (
                    self.db.query(LessonSection)
                    .join(Lesson)
                    .join(Topic)
                    .filter(Topic.course_id == course_id)
                    .count()
                )

                # Xóa khóa học (cascade sẽ tự động xóa topics, lessons, sections)
                self.db.delete(course)
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
                self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
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

        return {
            "deleted_count": len(deleted_courses),
            "failed_count": len(failed_courses),
            "deleted_courses": deleted_courses,
            "failed_courses": failed_courses,
            "errors": errors,
            "deleted_items": deleted_items,
        }

    def enroll_course(self, user_id: int, course_id: int):
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
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=404,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Kiểm tra xem người dùng đã đăng ký khóa học này chưa
            existing_enrollment = (
                self.db.query(UserCourse)
                .filter(
                    and_(
                        UserCourse.user_id == user_id, UserCourse.course_id == course_id
                    )
                )
                .first()
            )

            if existing_enrollment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Người dùng đã đăng ký khóa học này",
                )

            # Tạo đăng ký mới
            enrollment = UserCourse(user_id=user_id, course_id=course_id)
            self.db.add(enrollment)
            self.db.commit()
            self.db.refresh(enrollment)

            # Kiểm tra xem có test đầu vào cho khóa học này không
            from app.models.test_model import Test

            entry_test = self.db.query(Test).filter(Test.course_id == course_id).first()

            result = {
                "enrollment": enrollment,
                "has_entry_test": entry_test is not None,
                "entry_test_id": entry_test.id if entry_test else None,
            }

            return result
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi khi đăng ký khóa học: {str(e)}",
            )

    def get_user_courses(self, user_id: int):
        """
        Lấy danh sách khóa học mà người dùng đã đăng ký

        Args:
            user_id: ID của người dùng

        Returns:
            List[Course]: Danh sách khóa học
        """
        try:
            # Kiểm tra xem người dùng có tồn tại không
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=f"Không tìm thấy người dùng với ID {user_id}",
                )

            # Lấy danh sách khóa học mà người dùng đã đăng ký
            enrollments = (
                self.db.query(UserCourse).filter(UserCourse.user_id == user_id).all()
            )
            course_ids = [enrollment.course_id for enrollment in enrollments]
            courses = self.db.query(Course).filter(Course.id.in_(course_ids)).all()

            return courses
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
        enrollment = (
            self.db.query(UserCourse)
            .filter(
                and_(UserCourse.user_id == user_id, UserCourse.course_id == course_id)
            )
            .first()
        )
        return enrollment is not None

    def update_course_thumbnail(self, course_id: int, thumbnail_url: str):
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
            self.db.execute(
                text(
                    "UPDATE courses SET thumbnail_url = :thumbnail_url WHERE id = :course_id"
                ),
                {"thumbnail_url": thumbnail_url, "course_id": course_id},
            )
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi cập nhật ảnh thumbnail: {str(e)}",
            )

    def get_course_entry_test(self, course_id: int):
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
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Lấy test đầu vào
            from app.models.test_model import Test

            entry_test = self.db.query(Test).filter(Test.course_id == course_id).first()

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
        course = (
            self.db.query(Course)
            .options(selectinload(Course.topics).selectinload(Topic.lessons))
            .filter(Course.id == course_id)
            .first()
        )

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check enrollment
        user_course_id = None
        is_enrolled = False
        if user_id:
            user_course = (
                self.db.query(UserCourse)
                .filter(
                    UserCourse.user_id == user_id, UserCourse.course_id == course_id
                )
                .first()
            )
            if user_course:
                is_enrolled = True
                user_course_id = user_course.id

        # Get progress map
        progress_map = {}
        if user_course_id:
            progress_records = (
                self.db.query(UserCourseProgress)
                .filter(UserCourseProgress.user_course_id == user_course_id)
                .all()
            )
            progress_map = {(p.topic_id, p.lesson_id): p for p in progress_records}

        # Build enhanced topics with progress
        enhanced_topics = []
        total_lessons = 0
        completed_lessons = 0
        in_progress_lessons = 0
        not_started_lessons = 0
        current_topic_id = None
        current_lesson_id = None
        last_activity_at = None

        for topic in sorted(course.topics, key=lambda x: x.order or 0):
            # Build enhanced lessons for this topic
            enhanced_lessons = []
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

                enhanced_lessons.append(
                    LessonWithProgressResponse(
                        id=lesson.id,
                        external_id=lesson.external_id,
                        title=lesson.title,
                        description=lesson.description,
                        order=lesson.order,
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

            enhanced_topics.append(
                TopicWithProgressResponse(
                    id=topic.id,
                    external_id=topic.external_id,
                    name=topic.name,
                    description=topic.description,
                    order=topic.order,
                    lessons=enhanced_lessons,
                    topic_completion_percentage=round(topic_completion_percentage, 2),
                    completed_lessons=topic_completed,
                    total_lessons=topic_total,
                )
            )

        # Calculate overall completion percentage
        overall_completion_percentage = (
            (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
        )

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
            "topics": enhanced_topics,
            "user_course_id": user_course_id,
            "overall_completion_percentage": round(overall_completion_percentage, 2),
            "total_topics": len(enhanced_topics),
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "in_progress_lessons": in_progress_lessons,
            "not_started_lessons": not_started_lessons,
            "current_topic_id": current_topic_id,
            "current_lesson_id": current_lesson_id,
            "last_activity_at": last_activity_at,
        }

        return CourseDetailWithProgressResponse(**course_dict)

    async def get_topic_with_progress(
        self, topic_id: int, user_id: Optional[int] = None
    ) -> TopicDetailWithProgressResponse:
        """Lấy topic với nested lessons và progress"""
        # Get topic with lessons
        topic = (
            self.db.query(Topic)
            .options(selectinload(Topic.lessons))
            .filter(Topic.id == topic_id)
            .first()
        )

        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Check enrollment
        user_course_id = None
        if user_id:
            user_course = (
                self.db.query(UserCourse)
                .filter(
                    UserCourse.user_id == user_id,
                    UserCourse.course_id == topic.course_id,
                )
                .first()
            )
            if user_course:
                user_course_id = user_course.id

        # Get progress map for this topic
        progress_map = {}
        if user_course_id:
            progress_records = (
                self.db.query(UserCourseProgress)
                .filter(
                    UserCourseProgress.user_course_id == user_course_id,
                    UserCourseProgress.topic_id == topic_id,
                )
                .all()
            )
            progress_map = {p.lesson_id: p for p in progress_records}

        # Build enhanced lessons
        enhanced_lessons = []
        completed_lessons = 0

        for lesson in sorted(topic.lessons, key=lambda x: x.order):
            progress = progress_map.get(lesson.id)

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
                        50.0 if progress.status == ProgressStatus.IN_PROGRESS else 0.0
                    )
                )

                if lesson_status == ProgressStatus.COMPLETED:
                    completed_lessons += 1

            enhanced_lessons.append(
                LessonWithProgressResponse(
                    id=lesson.id,
                    external_id=lesson.external_id,
                    title=lesson.title,
                    description=lesson.description,
                    order=lesson.order,
                    status=lesson_status,
                    last_viewed_at=lesson_last_viewed,
                    completed_at=lesson_completed_at,
                    completion_percentage=lesson_completion,
                )
            )

        # Calculate topic completion percentage
        total_lessons = len(enhanced_lessons)
        topic_completion_percentage = (
            (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
        )

        return TopicDetailWithProgressResponse(
            id=topic.id,
            external_id=topic.external_id,
            name=topic.name,
            description=topic.description,
            order=topic.order,
            course_id=topic.course_id,
            lessons=enhanced_lessons,
            topic_completion_percentage=round(topic_completion_percentage, 2),
            completed_lessons=completed_lessons,
            total_lessons=total_lessons,
            user_course_id=user_course_id,
        )

    async def get_lesson_with_progress(
        self, lesson_id: int, user_id: Optional[int] = None
    ) -> LessonDetailWithProgressResponse:
        """Lấy lesson với progress"""
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()

        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        # Get topic and course info
        topic = self.db.query(Topic).filter(Topic.id == lesson.topic_id).first()

        # Check enrollment
        user_course_id = None
        if user_id and topic:
            user_course = (
                self.db.query(UserCourse)
                .filter(
                    UserCourse.user_id == user_id,
                    UserCourse.course_id == topic.course_id,
                )
                .first()
            )
            if user_course:
                user_course_id = user_course.id

        # Get progress for this lesson
        lesson_status = ProgressStatus.NOT_STARTED
        lesson_last_viewed = None
        lesson_completed_at = None
        lesson_completion = 0.0

        if user_course_id:
            progress = (
                self.db.query(UserCourseProgress)
                .filter(
                    UserCourseProgress.user_course_id == user_course_id,
                    UserCourseProgress.topic_id == lesson.topic_id,
                    UserCourseProgress.lesson_id == lesson_id,
                )
                .first()
            )

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
                        50.0 if progress.status == ProgressStatus.IN_PROGRESS else 0.0
                    )
                )

        return LessonDetailWithProgressResponse(
            id=lesson.id,
            external_id=lesson.external_id,
            title=lesson.title,
            description=lesson.description,
            order=lesson.order,
            topic_id=lesson.topic_id,
            status=lesson_status,
            last_viewed_at=lesson_last_viewed,
            completed_at=lesson_completed_at,
            completion_percentage=lesson_completion,
            user_course_id=user_course_id,
        )


def get_course_service(db: Session):
    """
    Factory function to get CourseService instance with database session and optional test generation service
    Note: Do NOT use Session as a response_model or return type in FastAPI routes. Only use Pydantic schemas or serializable types.
    """
    return CourseService(db)
