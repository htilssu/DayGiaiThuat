from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.database.database import get_async_db
from app.models.test_model import Test
from app.models.test_session import TestSession
from app.schemas.test_schema import (
    QuestionFeedback,
    TestCreate,
    TestHistorySummary,
    TestResult,
    TestSessionCreate,
    TestSessionUpdate,
    TestSubmission,
    TestUpdate,
)
from fastapi import Depends, HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession


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

    async def get_all_tests(self) -> List[Test]:
        """Lấy danh sách tất cả bài kiểm tra"""
        result = await self.session.execute(select(Test))
        return list(result.scalars().all())

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
                detail=f"Không tìm thấy bài kiểm tra với ID: {session_data.test_id}",
            )

        # Kiểm tra xem user có phiên làm bài thực sự đang hoạt động không
        has_active_session = await self.has_truly_active_session(session_data.user_id)

        if has_active_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bạn đang có một phiên làm bài kiểm tra khác đang hoạt động. Vui lòng hoàn thành hoặc hủy phiên đó trước khi bắt đầu phiên mới.",
            )

        # Tạo phiên mới (chưa bắt đầu - start_time = None)
        now = datetime.utcnow()
        test_session = TestSession(
            user_id=session_data.user_id,
            test_id=session_data.test_id,
            start_time=None,  # Chưa bắt đầu thực sự
            last_activity=now,
            time_remaining_seconds=test.duration_minutes * 60,
            status="pending",  # Trạng thái chưa bắt đầu
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
                TestSession.status.in_(["pending", "in_progress"]),
                TestSession.is_submitted == False,
            )
        )
        sessions = result.scalars().all()

        now = datetime.utcnow()

        # Kiểm tra từng session xem có thực sự active không
        for session in sessions:
            if self._is_session_truly_active(session, now):
                return session

        return None

    def _is_session_truly_active(self, session: TestSession, now: datetime) -> bool:
        """Helper method để kiểm tra session có thực sự đang hoạt động không"""
        if session.status == "pending":
            # Phiên pending: kiểm tra có quá 30 phút từ lúc tạo không
            time_since_created = now - session.created_at
            return time_since_created <= timedelta(minutes=30)

        elif session.status == "in_progress":
            # Phiên in_progress: kiểm tra có hết thời gian làm bài không
            if session.start_time:
                elapsed_seconds = (now - session.start_time).total_seconds()
                if elapsed_seconds >= session.time_remaining_seconds:
                    return False  # Đã hết thời gian làm bài

            # Kiểm tra thời gian không hoạt động
            inactive_time = now - session.last_activity
            if inactive_time > timedelta(minutes=30):
                return False  # Quá lâu không hoạt động

            return True

        return False

    async def get_user_sessions(self, user_id: int) -> List[TestSession]:
        """Lấy danh sách tất cả session của một user"""
        result = await self.session.execute(
            select(TestSession).where(TestSession.user_id == user_id)
        )
        return result.scalars().all()

    async def get_user_test_history(self, user_id: int) -> List[TestHistorySummary]:
        # Lấy tất cả test sessions của user
        result = await self.session.execute(
            select(TestSession)
            .where(TestSession.user_id == user_id)
            .order_by(TestSession.created_at.desc())
        )

        test_sessions = result.scalars().all()

        # Chuyển đổi thành TestHistorySummary
        history = []
        for test_session in test_sessions:
            try:
                # Tính thời gian làm bài
                duration_minutes = 0
                if test_session.start_time and test_session.end_time:
                    duration_delta = test_session.end_time - test_session.start_time
                    duration_minutes = max(0, int(duration_delta.total_seconds() / 60))

                summary = TestHistorySummary(
                    session_id=test_session.id,
                    test_id=test_session.test_id,
                    topic_id=None,  # Không lấy từ join
                    course_id=None,  # Không lấy từ join
                    test_name=f"Bài kiểm tra #{test_session.test_id}",  # Tên đơn giản
                    start_time=test_session.start_time,
                    end_time=test_session.end_time,
                    duration_minutes=duration_minutes,
                    score=test_session.score,
                    correct_answers=test_session.correct_answers,
                    total_questions=0,  # Có thể lấy từ test nếu cần
                    status=test_session.status,
                )
                history.append(summary)

            except Exception as e:
                # Log lỗi nhưng không làm fail toàn bộ request
                print(f"Error processing test session {test_session.id}: {str(e)}")
                continue

        return history

    async def get_test_session_detail(
        self, session_id: str, user_id: int
    ) -> Dict[str, Any]:
        """Lấy thông tin chi tiết của một phiên làm bài"""
        from app.models.course_model import Course
        from app.models.topic_model import Topic

        result = await self.session.execute(
            select(TestSession, Test, Topic, Course)
            .join(Test, TestSession.test_id == Test.id)
            .outerjoin(Topic, Test.topic_id == Topic.id)
            .outerjoin(Course, Test.course_id == Course.id)
            .where(TestSession.id == session_id)
        )

        session_data = result.first()
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phiên làm bài",
            )

        test_session, test, topic, course = session_data

        # Kiểm tra quyền truy cập
        if test_session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xem phiên làm bài này",
            )

        # Tên bài kiểm tra
        test_name = "Bài kiểm tra"
        if topic:
            test_name = f"Kiểm tra: {topic.name}"
        elif course:
            test_name = f"Bài kiểm tra đầu vào: {course.title}"

        # Tính thời gian làm bài
        start_time = test_session.start_time
        end_time = test_session.end_time or test_session.updated_at
        duration_minutes = 0

        if start_time and end_time:
            duration_delta = end_time - start_time
            duration_minutes = int(duration_delta.total_seconds() / 60)

        return {
            "sessionId": test_session.id,
            "testId": test_session.test_id,
            "userId": test_session.user_id,
            "testName": test_name,
            "startTime": start_time.isoformat() if start_time else None,
            "endTime": end_time.isoformat() if end_time else None,
            "durationMinutes": duration_minutes,
            "timeRemainingSeconds": test_session.time_remaining_seconds,
            "status": test_session.status,
            "isSubmitted": test_session.is_submitted,
            "currentQuestionIndex": test_session.current_question_index,
            "score": test_session.score,
            "correctAnswers": test_session.correct_answers,
            "totalQuestions": len(test.questions) if test.questions else 0,
            "answers": test_session.answers or {},
            "questions": test.questions or [],
            "topicId": test.topic_id,
            "courseId": test.course_id,
            "createdAt": (
                test_session.created_at.isoformat() if test_session.created_at else None
            ),
            "updatedAt": (
                test_session.updated_at.isoformat() if test_session.updated_at else None
            ),
        }

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

    async def count_expired_sessions(self) -> Dict[str, Any]:
        """Đếm số phiên làm bài đã hết hạn (không thay đổi status)"""
        # Lấy tất cả các phiên đang có status pending hoặc in_progress
        result = await self.session.execute(
            select(TestSession).where(
                and_(
                    TestSession.status.in_(["pending", "in_progress"]),
                    TestSession.is_submitted == False,
                )
            )
        )
        sessions = list(result.scalars().all())

        expired_count = 0
        expired_sessions = []
        now = datetime.utcnow()

        for session in sessions:
            is_expired = False
            reason = ""

            if session.status == "pending":
                # Phiên pending: kiểm tra thời gian từ lúc tạo
                time_since_created = now - session.created_at
                if time_since_created > timedelta(minutes=30):
                    is_expired = True
                    reason = f"Pending quá {int(time_since_created.total_seconds() / 60)} phút"

            elif session.status == "in_progress":
                # Phiên in_progress: kiểm tra theo nhiều tiêu chí

                # 1. Kiểm tra thời gian không hoạt động
                inactive_time = now - session.last_activity
                if inactive_time > timedelta(minutes=30):
                    is_expired = True
                    reason = f"Không hoạt động {int(inactive_time.total_seconds() / 60)} phút"

                # 2. Kiểm tra thời gian làm bài đã hết
                elif session.start_time:
                    elapsed_seconds = (now - session.start_time).total_seconds()
                    if elapsed_seconds >= session.time_remaining_seconds:
                        is_expired = True
                        remaining_minutes = max(
                            0,
                            int(
                                (session.time_remaining_seconds - elapsed_seconds) / 60
                            ),
                        )
                        reason = f"Hết thời gian làm bài (quá {int((elapsed_seconds - session.time_remaining_seconds) / 60)} phút)"

                # 3. Kiểm tra time_remaining_seconds đã <= 0
                elif session.time_remaining_seconds <= 0:
                    is_expired = True
                    reason = "time_remaining_seconds <= 0"

            if is_expired:
                expired_count += 1
                expired_sessions.append(
                    {
                        "session_id": session.id,
                        "user_id": session.user_id,
                        "test_id": session.test_id,
                        "status": session.status,
                        "reason": reason,
                        "created_at": session.created_at.isoformat(),
                    }
                )

        return {
            "total_sessions": len(sessions),
            "expired_count": expired_count,
            "expired_sessions": expired_sessions,
        }

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

        # Nếu session ở trạng thái pending (chưa bắt đầu)
        if session.status == "pending":
            # Kiểm tra có hết hạn thời gian pending không
            now = datetime.utcnow()
            time_since_created = now - session.created_at
            if time_since_created > timedelta(minutes=30):
                return {
                    "can_access": False,
                    "reason": "test_expired",
                    "message": "Phiên làm bài đã hết hạn thời gian pending",
                    "session": session,
                }
            return {
                "can_access": False,
                "reason": "not_started",
                "message": "Bài kiểm tra chưa được bắt đầu",
                "session": session,
            }

        # Kiểm tra session in_progress có thực sự còn active không
        if session.status == "in_progress":
            now = datetime.utcnow()
            if not self._is_session_truly_active(session, now):
                return {
                    "can_access": False,
                    "reason": "test_expired",
                    "message": "Bài kiểm tra đã hết thời gian",
                    "session": session,
                }

        return {"can_access": True, "session": session}

    async def start_test_session(self, session_id: str, user_id: int) -> TestSession:
        """Bắt đầu phiên làm bài thực sự - chuyển từ pending sang in_progress"""
        session = await self.get_test_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phiên làm bài",
            )

        # Kiểm tra quyền
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập phiên làm bài này",
            )

        # Chỉ có thể start session đang pending
        if session.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không thể bắt đầu phiên làm bài với trạng thái: {session.status}",
            )

        # Cập nhật session để bắt đầu
        now = datetime.utcnow()
        session.start_time = now
        session.last_activity = now
        session.status = "in_progress"

        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def has_truly_active_session(self, user_id: int) -> bool:
        """Kiểm tra xem user có phiên làm bài thực sự đang hoạt động không"""
        # Lấy tất cả session có trạng thái pending hoặc in_progress chưa submit
        result = await self.session.execute(
            select(TestSession).where(
                and_(
                    TestSession.user_id == user_id,
                    TestSession.status.in_(["pending", "in_progress"]),
                    TestSession.is_submitted == False,
                )
            )
        )
        sessions = result.scalars().all()

        now = datetime.utcnow()

        # Kiểm tra xem có session nào thực sự đang hoạt động không
        for session in sessions:
            if self._is_session_truly_active(session, now):
                return True

        return False  # Không có session nào thực sự đang hoạt động


def get_test_service(session: AsyncSession = Depends(get_async_db)):
    return TestService(session)
