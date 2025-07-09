from fastapi import Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.services.test_generation_service import (
    TestGenerationService,
    get_test_generation_service,
)

from app.database.database import get_db
from app.models.course_model import Course, TestGenerationStatus
from app.models.user_course_model import UserCourse
from app.models.user_model import User
from app.schemas.course_schema import CourseCreate


class CourseService:
    def __init__(
        self,
        db: Session,
        test_generation_service: TestGenerationService,
    ):
        self.db = db
        self.test_generation_service = test_generation_service

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

    def get_course(self, course_id: int):
        """
        Lấy thông tin chi tiết của một khóa học

        Args:
            course_id: ID của khóa học

        Returns:
            Course: Thông tin chi tiết của khóa học
        """
        return self.db.query(Course).filter(Course.id == course_id).first()

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
            course = self.get_course(course_id)
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
            course = self.get_course(course_id)
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
                course = self.get_course(course_id)
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
            # Kiểm tra xem người dùng có tồn tại không
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy người dùng với ID {user_id}",
                )

            # Kiểm tra xem khóa học có tồn tại không
            course = self.get_course(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi đăng ký khóa học: {str(e)}",
            )

    def unenroll_course(self, user_id: int, course_id: int):
        """
        Hủy đăng ký khóa học của người dùng

        Args:
            user_id: ID của người dùng
            course_id: ID của khóa học

        Returns:
            bool: True nếu hủy đăng ký thành công
        """
        try:
            # Tìm đăng ký cần hủy
            enrollment = (
                self.db.query(UserCourse)
                .filter(
                    and_(
                        UserCourse.user_id == user_id, UserCourse.course_id == course_id
                    )
                )
                .first()
            )

            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy đăng ký khóa học",
                )

            # Xóa đăng ký
            self.db.delete(enrollment)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi hủy đăng ký khóa học: {str(e)}",
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
                    status_code=status.HTTP_404_NOT_FOUND,
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

    def update_test_generation_status(self, course_id: int, status: str):
        """
        Cập nhật trạng thái tạo test cho khóa học

        Args:
            course_id: ID của khóa học
            status: Trạng thái mới
        """
        try:
            course = self.get_course(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            course.test_generation_status = status
            self.db.commit()
            self.db.refresh(course)

            return course
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi cập nhật trạng thái test: {str(e)}",
            )

    def generate_input_test_sync(self, course_id: int):
        """
        Tạo bài test đầu vào đồng bộ (sync) - Deprecated

        Sử dụng TestGenerationService thay thế
        """
        from app.services.test_generation_service import TestGenerationService

        test_gen_service = TestGenerationService(self.db)
        return test_gen_service.generate_input_test_sync(course_id)

    async def generate_input_test_async(self, course_id: int):
        """
        Tạo bài test đầu vào bất đồng bộ - Deprecated

        Sử dụng TestGenerationService thay thế
        """

        test_gen_service = TestGenerationService(self.db, self.test_generation_service)
        return await test_gen_service.generate_input_test_async(course_id)

    def _create_test_from_agent_sync(self, agent, course_id: int):
        """
        Tạo bài test từ agent và lưu vào database (phiên bản sync)

        Args:
            agent: Agent để tạo test
            course_id: ID của khóa học

        Returns:
            Test: Bài test đã được tạo
        """
        try:
            # Tạo test từ agent bằng asyncio.run() để chạy sync
            import asyncio

            test_result = asyncio.run(agent.act(course_id=course_id))

            # Lưu test vào database
            test = self._save_test_to_database_sync(course_id, test_result)

            return test

        except Exception as e:
            # Cập nhật trạng thái thất bại
            self.update_test_generation_status(course_id, TestGenerationStatus.FAILED)
            raise e

    async def _create_test_from_agent(self, agent, test_service, course_id: int):
        """
        Tạo bài test từ agent và lưu vào database

        Args:
            agent: Agent để tạo test
            test_service: Service để lưu test (không dùng nữa, để tương thích)
            course_id: ID của khóa học
        """
        try:
            # Tạo test từ agent
            test_result = await agent.act(course_id=course_id)

            # Chuyển đổi output từ agent thành format phù hợp để lưu vào database
            await self._save_test_to_database(None, course_id, test_result)

        except Exception as e:
            # Cập nhật trạng thái thất bại
            self.update_test_generation_status(course_id, TestGenerationStatus.FAILED)
            raise e

    def _save_test_to_database_sync(self, course_id: int, test_result):
        """
        Lưu kết quả test từ agent vào database (phiên bản sync)

        Args:
            course_id: ID của khóa học
            test_result: Kết quả từ agent (InputTestAgentOutput)

        Returns:
            Test: Bài test đã được lưu
        """
        try:
            # Lấy course để lấy thông tin
            course = self.get_course(course_id)
            if not course:
                raise ValueError(f"Không tìm thấy khóa học với ID {course_id}")

            # Chuyển đổi questions từ agent format sang database format (array)
            questions_list = []
            for i, question in enumerate(test_result.questions):
                question_id = f"q_{i + 1}"
                questions_list.append(
                    {
                        "id": question_id,
                        "content": question.content,
                        "type": question.type,
                        "difficulty": question.difficulty,
                        "answer": question.answer,
                        "options": question.options if question.options else [],
                    }
                )

            # Tạo test object và lưu vào database
            from app.models.test_model import Test

            test = Test(
                topic_id=None,  # Test thuộc về course, không thuộc về topic cụ thể
                course_id=course_id,  # Test thuộc về course này
                duration_minutes=60,  # Mặc định 60 phút
                questions=questions_list,
            )

            # Lưu bằng session sync
            self.db.add(test)
            self.db.commit()
            self.db.refresh(test)

            # Log thành công
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                f"Đã tạo thành công bài test ID {test.id} cho khóa học {course_id} (course: {course.title})"
            )

            return test

        except Exception as e:
            self.db.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Lỗi khi lưu test vào database: {e}", exc_info=True)
            raise e

    async def _save_test_to_database(self, test_service, course_id: int, test_result):
        """
        Lưu kết quả test từ agent vào database

        Args:
            test_service: Service để lưu test
            course_id: ID của khóa học
            test_result: Kết quả từ agent (InputTestAgentOutput)
        """
        try:
            # Lấy course để lấy thông tin
            course = self.get_course(course_id)
            if not course:
                raise ValueError(f"Không tìm thấy khóa học với ID {course_id}")

            # Chuyển đổi questions từ agent format sang database format (array)
            questions_list = []
            for i, question in enumerate(test_result.questions):
                question_id = f"q_{i + 1}"
                questions_list.append(
                    {
                        "id": question_id,
                        "content": question.content,
                        "type": question.type,
                        "difficulty": question.difficulty,
                        "answer": question.answer,
                        "options": question.options if question.options else [],
                    }
                )

            # Tạo test data để lưu vào database
            from app.schemas.test_schema import TestCreate

            test_data = TestCreate(
                topic_id=None,  # Test thuộc về course, không thuộc về topic cụ thể
                course_id=course_id,  # Test thuộc về course này
                duration_minutes=60,  # Mặc định 60 phút
                questions=questions_list,
            )

            # Lưu vào database (tạm thời dùng sync để tránh lỗi async session)
            from app.models.test_model import Test

            test = Test(
                topic_id=test_data.topic_id,
                course_id=test_data.course_id,
                duration_minutes=test_data.duration_minutes,
                questions=test_data.questions,
            )

            # Lưu bằng session sync
            self.db.add(test)
            self.db.commit()
            self.db.refresh(test)

            # Log thành công
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                f"Đã tạo thành công bài test ID {test.id} cho khóa học {course_id} (course: {course.title})"
            )

            return test

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Lỗi khi lưu test vào database: {e}", exc_info=True)
            raise e

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
            # Tìm khóa học cần cập nhật
            course = self.get_course(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Cập nhật URL thumbnail
            course.thumbnail_url = thumbnail_url

            # Lưu thay đổi vào database
            self.db.commit()
            self.db.refresh(course)

            return course
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
            course = self.get_course(course_id)
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


def get_course_service(
    db: Session = Depends(get_db),
    test_generation_service: TestGenerationService = Depends(
        get_test_generation_service
    ),
):
    return CourseService(db, test_generation_service)
