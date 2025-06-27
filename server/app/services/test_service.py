from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, update, and_
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
            topic_id=test_data.topic_id,
            course_id=test_data.course_id,
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
        test = result.scalars().first()

        # Migration: Convert questions from dict to array if needed
        if test and test.questions:

            if isinstance(test.questions, dict) and not isinstance(
                test.questions, list
            ):
                print("Converting questions from dict to array...")
                # Convert from dict format to array format
                questions_list = []
                for key, question in test.questions.items():
                    questions_list.append(question)

                # Update the test object and save to database
                await self.session.execute(
                    update(Test)
                    .where(Test.id == test_id)
                    .values(questions=questions_list)
                )
                await self.session.commit()

                # Update local object
                test.questions = questions_list
                print(f"Converted questions to array: {len(questions_list)} items")
            else:
                print("Questions already in correct format")

        return test

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

    async def create_test_session_from_course_entry_test(
        self, course_id: int, user_id: int
    ) -> TestSession:
        """Tạo một phiên làm bài kiểm tra đầu vào cho khóa học"""
        # Tìm test đầu vào của khóa học
        result = await self.session.execute(
            select(Test).where(Test.course_id == course_id)
        )
        entry_test = result.scalars().first()

        if not entry_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy bài kiểm tra đầu vào cho khóa học ID: {course_id}",
            )

        session_data = TestSessionCreate(user_id=user_id, test_id=entry_test.id)
        return await self.create_test_session(session_data)

    async def get_test_session(self, session_id: str) -> Optional[TestSession]:
        """Lấy thông tin phiên làm bài kiểm tra theo ID"""
        result = await self.session.execute(
            select(TestSession).where(TestSession.id == session_id)
        )
        test_session = result.scalars().first()

        return test_session

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
        """Lấy danh sách tất cả session của một user"""
        result = await self.session.execute(
            select(TestSession).where(TestSession.user_id == user_id)
        )
        return result.scalars().all()

    async def get_user_test_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Lấy lịch sử làm bài kiểm tra của người dùng với thông tin bài kiểm tra"""
        result = await self.session.execute(
            select(TestSession, Test)
            .join(Test, TestSession.test_id == Test.id)
            .where(
                and_(
                    TestSession.user_id == user_id,
                    TestSession.status.in_(["completed", "expired"]),
                )
            )
            .order_by(TestSession.start_time.desc())
        )

        history = []
        for test_session, test in result.all():
            # Tính thời gian làm bài
            start_time = test_session.start_time
            end_time = test_session.end_time or test_session.updated_at

            # Chuyển đổi sang dictionary và thêm thông tin test
            session_dict = {
                "id": test_session.id,
                "testId": test_session.test_id,
                "userId": test_session.user_id,
                "startTime": start_time.isoformat() if start_time else None,
                "endTime": end_time.isoformat() if end_time else None,
                "timeRemainingSeconds": test_session.time_remaining_seconds,
                "status": test_session.status,
                "isSubmitted": test_session.is_submitted,
                "currentQuestionIndex": test_session.current_question_index,
                "score": test_session.score,
                "correctAnswers": test_session.correct_answers,
                "answers": test_session.answers or {},
                "createdAt": (
                    test_session.created_at.isoformat()
                    if test_session.created_at
                    else None
                ),
                "updatedAt": (
                    test_session.updated_at.isoformat()
                    if test_session.updated_at
                    else None
                ),
                "test": {
                    "id": test.id,
                    "name": test.name,
                    "description": test.description,
                    "questions": test.questions,
                    "durationMinutes": test.duration_minutes,
                    "passingScore": test.passing_score,
                    "difficulty": getattr(test, "difficulty", None),
                    "topicName": getattr(test, "topic_name", None),
                    "courseName": getattr(test, "course_name", None),
                },
            }
            history.append(session_dict)

        return history

    async def update_session(
        self, session_id: str, update_data: TestSessionUpdate
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
        self, session_id: str, question_id: str, answer: Any
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
        self,
        session_id: str,
        submission: Optional[TestSubmission] = None,
        is_auto_submit: bool = False,
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
        if is_auto_submit:
            session.status = "expired"  # Mark as expired for auto-submit
        else:
            session.status = "completed"  # Mark as completed for manual submit
        session.is_submitted = True
        session.score = result.score
        session.correct_answers = result.correct_answers

        await self.session.commit()
        await self.session.refresh(session)

        return result

    def _calculate_score(self, questions: Any, answers: Dict[str, Any]) -> TestResult:
        """Tính điểm cho bài kiểm tra"""
        # Trong thực tế, đây sẽ là logic phức tạp để chấm điểm dựa trên loại câu hỏi
        # Đây chỉ là một triển khai đơn giản

        # Handle both dict and list formats
        questions_list = []
        if isinstance(questions, list):
            questions_list = questions
        elif isinstance(questions, dict):
            # Convert dict to list for backward compatibility
            questions_list = list(questions.values())

        total_questions = len(questions_list)
        if total_questions == 0:
            return TestResult(
                score=0, total_questions=0, correct_answers=0, feedback={}
            )

        correct_count = 0
        feedback = {}

        for question in questions_list:
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

    async def can_access_test_session(
        self, session_id: str, user_id: int
    ) -> Dict[str, Any]:
        """Kiểm tra xem người dùng có thể truy cập phiên làm bài hay không"""
        session = await self.get_test_session(session_id)

        if not session:
            return {
                "can_access": False,
                "reason": "session_not_found",
                "message": "Không tìm thấy phiên làm bài",
            }

        if session.user_id != user_id:
            return {
                "can_access": False,
                "reason": "permission_denied",
                "message": "Không có quyền truy cập phiên làm bài này",
            }

        if session.status == "completed":
            return {
                "can_access": False,
                "reason": "test_completed",
                "message": "Bài kiểm tra đã được hoàn thành",
                "session": session,
            }

        if session.status == "expired":
            return {
                "can_access": False,
                "reason": "test_expired",
                "message": "Bài kiểm tra đã hết thời gian",
                "session": session,
            }

        # Check if time has expired based on start time and duration
        if session.start_time:
            elapsed_seconds = (datetime.utcnow() - session.start_time).total_seconds()
            if elapsed_seconds >= session.time_remaining_seconds:
                # Auto-expire the session
                session.status = "expired"
                await self.session.commit()
                return {
                    "can_access": False,
                    "reason": "test_expired",
                    "message": "Bài kiểm tra đã hết thời gian",
                    "session": session,
                }

        return {"can_access": True, "session": session}


def get_test_service(session: AsyncSession = Depends(get_async_session)):
    return TestService(session)
