"""
Service chuyên dụng cho việc tạo bài test
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import asyncio
import logging

from app.database.database import get_db
from app.models.course_model import Course, TestGenerationStatus
from app.models.test_model import Test


class TestGenerationService:
    """Service chuyên dụng cho việc tạo bài test"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def generate_input_test_sync(self, course_id: int):
        """
        Tạo bài test đầu vào đồng bộ (sync)

        Args:
            course_id: ID của khóa học

        Returns:
            Test: Bài test đã được tạo và lưu vào database

        Raises:
            HTTPException: Nếu có lỗi trong quá trình tạo test
        """
        try:
            # Cập nhật trạng thái thành pending
            self._update_test_generation_status(course_id, TestGenerationStatus.PENDING)

            # Import agent để tránh circular dependency
            from app.core.agents.input_test_agent import get_input_test_agent

            # Tạo test agent
            agent = get_input_test_agent(self)

            # Tạo test đồng bộ
            test = self._create_test_from_agent_sync(agent, course_id)

            # Cập nhật trạng thái thành công
            self._update_test_generation_status(course_id, TestGenerationStatus.SUCCESS)

            return test

        except Exception as e:
            # Cập nhật trạng thái thất bại
            self._update_test_generation_status(course_id, TestGenerationStatus.FAILED)

            # Log lỗi
            self.logger.error(
                f"Lỗi khi tạo test cho khóa học {course_id}: {e}", exc_info=True
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi tạo bài test: {str(e)}",
            )

    async def generate_input_test_async(self, course_id: int):
        """
        Tạo bài test đầu vào bất đồng bộ

        Args:
            course_id: ID của khóa học
        """

        def run_in_thread():
            try:
                # Update status to pending
                self._update_test_generation_status(
                    course_id, TestGenerationStatus.PENDING
                )

                # Import agent here to avoid circular dependency
                from app.core.agents.input_test_agent import get_input_test_agent

                # Create test agent and generate test
                agent = get_input_test_agent(self)

                # This would be the actual test generation logic
                asyncio.run(self._create_test_from_agent_async(agent, course_id))

                # Update status to success
                self._update_test_generation_status(
                    course_id, TestGenerationStatus.SUCCESS
                )

            except Exception as e:
                # Update status to failed
                self._update_test_generation_status(
                    course_id, TestGenerationStatus.FAILED
                )

                # Log error với thông tin chi tiết
                self.logger.error(
                    f"Lỗi khi tạo test cho khóa học {course_id}: {e}", exc_info=True
                )

                print(f"Error generating test for course {course_id}: {e}")

        # Run in background thread
        import threading

        thread = threading.Thread(target=run_in_thread)
        thread.start()

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
            test_result = asyncio.run(agent.act(course_id=course_id))

            # Lưu test vào database
            test = self._save_test_to_database_sync(course_id, test_result)

            return test

        except Exception as e:
            # Cập nhật trạng thái thất bại
            self._update_test_generation_status(course_id, TestGenerationStatus.FAILED)
            raise e

    async def _create_test_from_agent_async(self, agent, course_id: int):
        """
        Tạo bài test từ agent và lưu vào database (phiên bản async)

        Args:
            agent: Agent để tạo test
            course_id: ID của khóa học
        """
        try:
            # Tạo test từ agent
            test_result = await agent.act(course_id=course_id)

            # Chuyển đổi output từ agent thành format phù hợp để lưu vào database
            await self._save_test_to_database_async(course_id, test_result)

        except Exception as e:
            # Cập nhật trạng thái thất bại
            self._update_test_generation_status(course_id, TestGenerationStatus.FAILED)
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
            self.logger.info(
                f"Đã tạo thành công bài test ID {test.id} cho khóa học {course_id} (course: {course.title})"
            )

            return test

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Lỗi khi lưu test vào database: {e}", exc_info=True)
            raise e

    async def _save_test_to_database_async(self, course_id: int, test_result):
        """
        Lưu kết quả test từ agent vào database (phiên bản async)

        Args:
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

            # Tạo test object và lưu vào database
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
            self.logger.info(
                f"Đã tạo thành công bài test ID {test.id} cho khóa học {course_id} (course: {course.title})"
            )

            return test

        except Exception as e:
            self.logger.error(f"Lỗi khi lưu test vào database: {e}", exc_info=True)
            raise e

    def get_course(self, course_id: int):
        """
        Lấy thông tin chi tiết của một khóa học

        Args:
            course_id: ID của khóa học

        Returns:
            Course: Thông tin chi tiết của khóa học
        """
        return self.db.query(Course).filter(Course.id == course_id).first()

    def _update_test_generation_status(self, course_id: int, status: str):
        """
        Cập nhật trạng thái tạo test cho khóa học

        Args:
            course_id (int): ID của khóa học
            status (str): Trạng thái mới

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

            course.test_generation_status = status
            self.db.commit()
            self.db.refresh(course)

            return course
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Lỗi khi cập nhật trạng thái test: {str(e)}")
            # Không raise HTTPException ở đây vì đây là internal method
            pass

    def get_test_generation_status(self, course_id: int):
        """
        Lấy trạng thái tạo test của khóa học

        Args:
            course_id: ID của khóa học

        Returns:
            str: Trạng thái hiện tại
        """
        course = self.get_course(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )
        return course.test_generation_status

    def get_course_tests(self, course_id: int):
        """
        Lấy danh sách test của khóa học

        Args:
            course_id: ID của khóa học

        Returns:
            List[Test]: Danh sách test
        """
        return self.db.query(Test).filter(Test.course_id == course_id).all()

    def get_test_by_id(self, test_id: int):
        """
        Lấy test theo ID

        Args:
            test_id: ID của test

        Returns:
            Test: Thông tin test
        """
        return self.db.query(Test).filter(Test.id == test_id).first()

    def delete_test(self, test_id: int):
        """
        Xóa test

        Args:
            test_id: ID của test

        Returns:
            bool: True nếu xóa thành công
        """
        try:
            test = self.get_test_by_id(test_id)
            if not test:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy test với ID {test_id}",
                )

            self.db.delete(test)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi xóa test: {str(e)}",
            )


def get_test_generation_service(db: Session = Depends(get_db)):
    """Dependency để inject TestGenerationService"""
    return TestGenerationService(db)
