from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_session
from app.models.test_model import Test
from app.models.test_session import TestSession
from app.schemas.test_schema import (
    TestCreate,
    TestUpdate,
    TestSessionCreate,
    TestSessionUpdate,
    TestSubmission,
    TestResult,
    QuestionFeedback,
)


class TestService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_test(self, test_data: TestCreate) -> Test:
        """Tạo một bài kiểm tra mới"""
        test = Test(
            name=test_data.name,
            description=test_data.description,
            topic_id=test_data.topic_id,
            duration_minutes=test_data.duration_minutes,
            questions=test_data.questions,
        )
        self.session.add(test)
        await self.session.commit()
        await self.session.refresh(test)
        return test

    async def get_test(self, test_id: int) -> Optional[Test]:
        """Lấy thông tin bài kiểm tra theo ID"""
        result = await self.session.execute(select(Test).where(Test.id == test_id))
        return result.scalars().first()

    async def get_tests_by_topic(self, topic_id: int) -> List[Test]:
        """Lấy danh sách bài kiểm tra theo topic"""
        result = await self.session.execute(
            select(Test).where(Test.topic_id == topic_id)
        )
        return list(result.scalars().all())

    async def update_test(self, test_id: int, test_data: TestUpdate) -> Optional[Test]:
        """Cập nhật thông tin bài kiểm tra"""
        test = await self.get_test(test_id)
        if not test:
            return None

        update_data = test_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(test, key, value)

        await self.session.commit()
        await self.session.refresh(test)
        return test

    async def delete_test(self, test_id: int) -> bool:
        """Xóa bài kiểm tra"""
        test = await self.get_test(test_id)
        if not test:
            return False

        await self.session.delete(test)
        await self.session.commit()
        return True

    async def create_test_session(self, session_data: TestSessionCreate) -> TestSession:
        """Tạo một phiên làm bài kiểm tra mới"""
        # Kiểm tra xem bài kiểm tra có tồn tại không
        test = await self.get_test(session_data.test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy bài kiểm tra",
            )

        # Kiểm tra xem người dùng có phiên làm bài nào đang hoạt động không
        # Đầu tiên, kiểm tra phiên làm bài cho cùng một bài kiểm tra
        active_session = await self.get_active_session(
            session_data.user_id, session_data.test_id
        )
        if active_session:
            return active_session

        # Kiểm tra xem người dùng có phiên làm bài nào khác đang hoạt động không
        result = await self.session.execute(
            select(TestSession).where(
                TestSession.user_id == session_data.user_id,
                TestSession.status == "in_progress",
                TestSession.is_submitted == False,
            )
        )
        other_active_sessions = list(result.scalars().all())

        if other_active_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bạn đang có một phiên làm bài kiểm tra khác đang hoạt động. Vui lòng hoàn thành hoặc hủy phiên đó trước khi bắt đầu phiên mới.",
            )

        # Tạo phiên mới
        now = datetime.utcnow()
        test_session = TestSession(
            user_id=session_data.user_id,
            test_id=session_data.test_id,
            start_time=now,
            last_activity=now,
            time_remaining_seconds=test.duration_minutes * 60,
            status="in_progress",
            is_submitted=False,
            current_question_index=0,
            answers={},
        )
        self.session.add(test_session)
        await self.session.commit()
        await self.session.refresh(test_session)
        return test_session

    async def create_test_session_from_topic(
        self, topic_id: int, user_id: int
    ) -> TestSession:
        """Tạo một phiên làm bài kiểm tra mới từ một topic"""
        tests = await self.get_tests_by_topic(topic_id)
        if not tests:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy bài kiểm tra nào cho topic_id: {topic_id}",
            )

        # Tạm thời chọn bài kiểm tra đầu tiên trong danh sách
        # Trong thực tế, có thể có logic phức tạp hơn để chọn hoặc tạo bài kiểm tra
        selected_test = tests[0]

        session_data = TestSessionCreate(user_id=user_id, test_id=selected_test.id)
        return await self.create_test_session(session_data)

    async def get_test_session(self, session_id: int) -> Optional[TestSession]:
        """Lấy thông tin phiên làm bài kiểm tra theo ID"""
        result = await self.session.execute(
            select(TestSession).where(TestSession.id == session_id)
        )
        return result.scalars().first()

    async def get_active_session(
        self, user_id: int, test_id: int
    ) -> Optional[TestSession]:
        """Lấy phiên làm bài đang hoạt động của người dùng cho một bài kiểm tra cụ thể"""
        result = await self.session.execute(
            select(TestSession).where(
                TestSession.user_id == user_id,
                TestSession.test_id == test_id,
                TestSession.status == "in_progress",
                TestSession.is_submitted == False,
            )
        )
        return result.scalars().first()

    async def get_user_sessions(self, user_id: int) -> List[TestSession]:
        """Lấy danh sách các phiên làm bài của người dùng"""
        result = await self.session.execute(
            select(TestSession).where(TestSession.user_id == user_id)
        )
        return list(result.scalars().all())

    async def update_session(
        self, session_id: int, update_data: TestSessionUpdate
    ) -> Optional[TestSession]:
        """Cập nhật thông tin phiên làm bài"""
        session = await self.get_test_session(session_id)
        if not session:
            return None

        # Kiểm tra xem phiên có đang hoạt động không
        if session.status != "in_progress" or session.is_submitted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể cập nhật phiên làm bài đã kết thúc",
            )

        # Cập nhật thời gian hoạt động cuối cùng
        session.last_activity = datetime.utcnow()

        # Cập nhật các trường khác
        data_dict = update_data.dict(exclude_unset=True)
        for key, value in data_dict.items():
            setattr(session, key, value)

        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def update_session_answer(
        self, session_id: int, question_id: str, answer: Any
    ) -> Optional[TestSession]:
        """Cập nhật câu trả lời cho một câu hỏi trong phiên làm bài"""
        session = await self.get_test_session(session_id)
        if not session:
            return None

        # Kiểm tra xem phiên có đang hoạt động không
        if session.status != "in_progress" or session.is_submitted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể cập nhật câu trả lời cho phiên làm bài đã kết thúc",
            )

        # Cập nhật câu trả lời
        answers = session.answers or {}
        answers[question_id] = answer
        session.answers = answers
        session.last_activity = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def submit_test_session(
        self, session_id: int, submission: Optional[TestSubmission] = None
    ) -> TestResult:
        """Nộp bài kiểm tra và tính điểm"""
        session = await self.get_test_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phiên làm bài",
            )

        # Kiểm tra xem phiên có đang hoạt động không
        if session.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phiên làm bài đã kết thúc",
            )

        # Cập nhật câu trả lời nếu có
        if submission and submission.answers:
            session.answers = submission.answers

        # Lấy thông tin bài kiểm tra
        test = await self.get_test(session.test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy bài kiểm tra",
            )

        # Tính điểm
        result = self._calculate_score(test.questions, session.answers)

        # Cập nhật thông tin phiên làm bài
        session.end_time = datetime.utcnow()
        session.status = "completed"
        session.is_submitted = True
        session.score = result.score
        session.correct_answers = result.correct_answers

        await self.session.commit()
        await self.session.refresh(session)

        return result

    def _calculate_score(
        self, questions: Dict[str, Any], answers: Dict[str, Any]
    ) -> TestResult:
        """Tính điểm cho bài kiểm tra"""
        # Trong thực tế, đây sẽ là logic phức tạp để chấm điểm dựa trên loại câu hỏi
        # Đây chỉ là một triển khai đơn giản
        total_questions = len(questions) if isinstance(questions, list) else 0
        if total_questions == 0:
            return TestResult(
                score=0, total_questions=0, correct_answers=0, feedback={}
            )

        correct_count = 0
        feedback = {}

        for question in questions:
            question_id = question.get("id", "")
            if not question_id or question_id not in answers:
                feedback[question_id] = QuestionFeedback(
                    is_correct=False, feedback="Không có câu trả lời"
                )
                continue

            # Đây là logic giả định, cần được thay thế bằng logic thực tế
            is_correct = self._check_answer(question, answers[question_id])
            if is_correct:
                correct_count += 1
                feedback[question_id] = QuestionFeedback(
                    is_correct=True, feedback="Câu trả lời đúng"
                )
            else:
                feedback[question_id] = QuestionFeedback(
                    is_correct=False, feedback="Câu trả lời sai"
                )

        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        return TestResult(
            score=score,
            total_questions=total_questions,
            correct_answers=correct_count,
            feedback=feedback,
        )

    def _check_answer(self, question: Dict[str, Any], answer: Any) -> bool:
        """Kiểm tra câu trả lời có đúng không"""
        # Đây là logic giả định, cần được thay thế bằng logic thực tế
        question_type = question.get("type", "")

        if question_type == "multiple_choice":
            correct_option = question.get("correct_option", "")
            return answer == correct_option
        elif question_type == "problem":
            # Đối với câu hỏi lập trình, cần có logic phức tạp hơn để kiểm tra
            # Có thể sử dụng agent hoặc dịch vụ bên ngoài để đánh giá
            return False  # Placeholder

        return False

    async def check_and_update_expired_sessions(self) -> int:
        """Kiểm tra và cập nhật các phiên làm bài đã hết hạn"""
        # Lấy tất cả các phiên đang hoạt động
        result = await self.session.execute(
            select(TestSession).where(
                TestSession.status == "in_progress", TestSession.is_submitted == False
            )
        )
        active_sessions = list(result.scalars().all())

        expired_count = 0
        now = datetime.utcnow()

        for session in active_sessions:
            # Kiểm tra thời gian không hoạt động
            inactive_time = now - session.last_activity
            if inactive_time > timedelta(minutes=30):  # 30 phút không hoạt động
                session.status = "expired"
                expired_count += 1

            # Kiểm tra thời gian còn lại
            if session.time_remaining_seconds <= 0:
                session.status = "expired"
                expired_count += 1

        if expired_count > 0:
            await self.session.commit()

        return expired_count


def get_test_service(session: AsyncSession = Depends(get_async_session)):
    return TestService(session)
