
import logging

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agents.test_generate_agent import (
    get_input_test_agent,
    InputTestAgent,
)
from app.database.database import get_independent_db_session
from app.models.course_model import Course, TestGenerationStatus
from app.models.test_model import Test


class TestGenerationService:

    def __init__(self):
        self.input_test_agent = InputTestAgent()
        self.logger = logging.getLogger(__name__)

    async def generate_input_test_async(self, course_id: int):
        import asyncio

        async def run_background_task():
            try:
                async with get_independent_db_session() as db:
                    await self.input_test_agent.act()
            except Exception as e:
                self.logger.error(f"Lỗi khi chạy tác vụ nền: {e}", exc_info=True)
                raise e

        asyncio.create_task(run_background_task())

    async def _save_test_to_database_async(self, course_id: int, test_result):
        try:
            course = await self.get_course(course_id)
            if not course:
                raise ValueError(f"Không tìm thấy khóa học với ID {course_id}")

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

            test = Test(
                topic_id=None,
                course_id=course_id,
                duration_minutes=60,
                questions=questions_list,
            )

            self.db.add(test)
            await self.db.commit()
            await self.db.refresh(test)

            self.logger.info(
                f"Đã tạo thành công bài test ID {test.id} cho khóa học {course_id} (course: {course.title})"
            )

            return test

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Lỗi khi lưu test vào database: {e}", exc_info=True)
            raise e

    async def get_course(self, course_id: int):
        from sqlalchemy import select

        result = await self.db.execute(select(Course).filter(Course.id == course_id))
        return result.scalar_one_or_none()

    async def _update_test_generation_status(self, course_id: int, status: str):
        try:
            course = await self.get_course(course_id)
            if not course:
                from fastapi import status as http_status

                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            course.test_generation_status = status
            await self.db.commit()
            await self.db.refresh(course)

            return course
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Lỗi khi cập nhật trạng thái test: {str(e)}")
            pass

    async def get_test_generation_status(self, course_id: int):
        course = await self.get_course(course_id)
        if not course:
            from fastapi import status as http_status

            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )
        return course.test_generation_status

    async def get_course_tests(self, course_id: int):
        from sqlalchemy import select

        result = await self.db.execute(select(Test).filter(Test.course_id == course_id))
        return result.scalars().all()

    async def get_test_by_id(self, test_id: int):
        from sqlalchemy import select

        result = await self.db.execute(select(Test).filter(Test.id == test_id))
        return result.scalar_one_or_none()

    async def delete_test(self, test_id: int):

        try:
            test = await self.get_test_by_id(test_id)
            if not test:
                from fastapi import status as http_status

                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy test với ID {test_id}",
                )

            await self.db.delete(test)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            from fastapi import status as http_status

            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi xóa test: {str(e)}",
            )


async def get_test_generation_service(
    test_generation_agent: InputTestAgent = Depends(get_input_test_agent),
):
    async with get_independent_db_session() as db:
        return TestGenerationService(db, test_generation_agent)
