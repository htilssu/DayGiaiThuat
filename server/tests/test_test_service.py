"""
Tests for Test Service functionality
"""
import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.test_service import TestService
from app.models.test_model import Test
from app.models.test_session import TestSession
from app.schemas.test_schema import (
    TestCreate,
    TestSessionCreate,
    TestSubmission,
    TestResult,
    QuestionFeedback,
)
from fastapi import HTTPException


class TestTestService:
    """Test class for TestService"""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def test_service(self, mock_session):
        """Create TestService instance with mocked session"""
        return TestService(mock_session)

    @pytest.fixture
    def sample_test_data(self):
        """Sample test data for testing"""
        return TestCreate(
            topic_id=1,
            course_id=None,
            duration_minutes=60,
            questions=[
                {
                    "id": "q1",
                    "content": "What is 2+2?",
                    "type": "multiple_choice",
                    "options": ["2", "3", "4", "5"],
                    "correct_option": "4"
                },
                {
                    "id": "q2",
                    "content": "Write a function to sum an array",
                    "type": "problem",
                    "answer": "function sumArray(arr) { return arr.reduce((a, b) => a + b, 0); }"
                }
            ]
        )

    @pytest.fixture
    def sample_test_model(self, sample_test_data):
        """Sample Test model instance"""
        test = Test(
            id=1,
            topic_id=sample_test_data.topic_id,
            course_id=sample_test_data.course_id,
            duration_minutes=sample_test_data.duration_minutes,
            questions=sample_test_data.questions
        )
        return test

    @pytest.fixture
    def sample_session_data(self):
        """Sample test session creation data"""
        return TestSessionCreate(
            user_id=1,
            test_id=1
        )

    @pytest.fixture
    def sample_test_session(self):
        """Sample TestSession model instance"""
        return TestSession(
            id="test-session-123",
            user_id=1,
            test_id=1,
            start_time=datetime.now(),
            time_remaining_seconds=3600,
            status="in_progress",
            is_submitted=False,
            current_question_index=0,
            answers={}
        )

    @pytest.mark.asyncio
    async def test_create_test(self, test_service, mock_session, sample_test_data):
        """Test creating a new test"""
        # Setup mock
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Execute
        result = await test_service.create_test(sample_test_data)

        # Verify
        assert isinstance(result, Test)
        assert result.topic_id == sample_test_data.topic_id
        assert result.duration_minutes == sample_test_data.duration_minutes
        assert result.questions == sample_test_data.questions
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_test_existing(self, test_service, mock_session, sample_test_model):
        """Test getting an existing test"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = sample_test_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Execute
        result = await test_service.get_test(1)

        # Verify
        assert result == sample_test_model
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_test_not_found(self, test_service, mock_session):
        """Test getting a non-existent test"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Execute
        result = await test_service.get_test(999)

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_create_test_session(self, test_service, mock_session, sample_session_data, sample_test_model):
        """Test creating a new test session"""
        # Setup mocks for get_test
        mock_get_test_result = Mock()
        mock_get_test_result.scalars.return_value.first.return_value = sample_test_model
        
        # Setup mocks for has_truly_active_session - need to return an empty list for sessions
        mock_active_session_result = Mock()
        mock_active_session_result.scalars.return_value.all.return_value = []  # Empty list of sessions
        
        mock_session.execute = AsyncMock(side_effect=[mock_get_test_result, mock_active_session_result])
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Execute
        result = await test_service.create_test_session(sample_session_data)

        # Verify
        assert isinstance(result, TestSession)
        assert result.user_id == sample_session_data.user_id
        assert result.test_id == sample_session_data.test_id
        assert result.status == "pending"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_test_session_test_not_found(self, test_service, mock_session, sample_session_data):
        """Test creating test session when test doesn't exist"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await test_service.create_test_session(sample_session_data)
        
        assert exc_info.value.status_code == 404
        assert "Không tìm thấy bài kiểm tra" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_test_session(self, test_service, mock_session, sample_test_session):
        """Test getting an existing test session"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = sample_test_session
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Execute
        result = await test_service.get_test_session("test-session-123")

        # Verify
        assert result == sample_test_session

    @pytest.mark.asyncio
    async def test_submit_test_session(self, test_service, mock_session, sample_test_session, sample_test_model):
        """Test submitting a test session"""
        # Setup test session with answers
        sample_test_session.answers = {
            "q1": "4",  # Simple answer format for multiple choice
            "q2": "function sumArray(arr) { return arr.reduce((a, b) => a + b, 0); }"
        }
        
        # Setup mocks
        mock_get_session_result = Mock()
        mock_get_session_result.scalars.return_value.first.return_value = sample_test_session
        
        mock_get_test_result = Mock()
        mock_get_test_result.scalars.return_value.first.return_value = sample_test_model
        
        mock_session.execute = AsyncMock(side_effect=[mock_get_session_result, mock_get_test_result])
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create submission
        submission = TestSubmission(answers=sample_test_session.answers)

        # Execute
        result = await test_service.submit_test_session("test-session-123", submission)

        # Verify
        assert isinstance(result, TestResult)
        assert result.total_questions == 2
        assert sample_test_session.status == "completed"
        assert sample_test_session.is_submitted is True
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_test_session_not_found(self, test_service, mock_session):
        """Test submitting a non-existent test session"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await test_service.submit_test_session("non-existent")
        
        assert exc_info.value.status_code == 404
        assert "Không tìm thấy phiên làm bài" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_test_session_already_completed(self, test_service, mock_session, sample_test_session):
        """Test submitting an already completed test session"""
        # Setup completed session
        sample_test_session.status = "completed"
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = sample_test_session
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await test_service.submit_test_session("test-session-123")
        
        assert exc_info.value.status_code == 400
        assert "Phiên làm bài đã kết thúc" in str(exc_info.value.detail)

    def test_calculate_score_correct_answers(self, test_service):
        """Test score calculation with correct answers"""
        questions = [
            {
                "id": "q1",
                "content": "What is 2+2?",
                "type": "multiple_choice",
                "options": ["2", "3", "4", "5"],
                "correct_option": "4"
            },
            {
                "id": "q2", 
                "content": "What is 3+3?",
                "type": "multiple_choice",
                "options": ["5", "6", "7", "8"],
                "correct_option": "6"
            }
        ]
        
        answers = {
            "q1": "4",
            "q2": "6"
        }

        result = test_service._calculate_score(questions, answers)

        assert result.score == 100.0
        assert result.total_questions == 2
        assert result.correct_answers == 2
        assert len(result.feedback) == 2
        assert result.feedback["q1"].is_correct is True
        assert result.feedback["q2"].is_correct is True

    def test_calculate_score_partial_correct(self, test_service):
        """Test score calculation with partially correct answers"""
        questions = [
            {
                "id": "q1",
                "content": "What is 2+2?",
                "type": "multiple_choice", 
                "options": ["2", "3", "4", "5"],
                "correct_option": "4"
            },
            {
                "id": "q2",
                "content": "What is 3+3?",
                "type": "multiple_choice",
                "options": ["5", "6", "7", "8"], 
                "correct_option": "6"
            }
        ]
        
        answers = {
            "q1": "4",  # Correct
            "q2": "7"   # Incorrect
        }

        result = test_service._calculate_score(questions, answers)

        assert result.score == 50.0
        assert result.total_questions == 2
        assert result.correct_answers == 1
        assert result.feedback["q1"].is_correct is True
        assert result.feedback["q2"].is_correct is False

    def test_calculate_score_no_answers(self, test_service):
        """Test score calculation with no answers provided"""
        questions = [
            {
                "id": "q1",
                "content": "What is 2+2?",
                "type": "multiple_choice",
                "options": ["2", "3", "4", "5"],
                "correct_option": "4"
            }
        ]
        
        answers = {}

        result = test_service._calculate_score(questions, answers)

        assert result.score == 0.0
        assert result.total_questions == 1
        assert result.correct_answers == 0
        assert result.feedback["q1"].is_correct is False
        assert "Không có câu trả lời" in result.feedback["q1"].feedback

    def test_calculate_score_empty_questions(self, test_service):
        """Test score calculation with no questions"""
        questions = []
        answers = {}

        result = test_service._calculate_score(questions, answers)

        assert result.score == 0.0
        assert result.total_questions == 0
        assert result.correct_answers == 0
        assert len(result.feedback) == 0

    @pytest.mark.asyncio
    async def test_auto_submit_expired_session(self, test_service, mock_session, sample_test_session, sample_test_model):
        """Test auto-submitting an expired session"""
        # Setup expired session
        sample_test_session.answers = {"q1": "4"}
        
        # Setup mocks
        mock_get_session_result = Mock()
        mock_get_session_result.scalars.return_value.first.return_value = sample_test_session
        
        mock_get_test_result = Mock()
        mock_get_test_result.scalars.return_value.first.return_value = sample_test_model
        
        mock_session.execute = AsyncMock(side_effect=[mock_get_session_result, mock_get_test_result])
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create submission for auto-submit
        submission = TestSubmission(answers=sample_test_session.answers)

        # Execute
        result = await test_service.submit_test_session("test-session-123", submission, is_auto_submit=True)

        # Verify
        assert isinstance(result, TestResult)
        assert sample_test_session.status == "expired"  # Should be marked as expired for auto-submit
        assert sample_test_session.is_submitted is True
        mock_session.commit.assert_called_once()


class TestCodeRunner:
    """Test the frontend code runner functionality"""

    def test_run_tests_with_correct_code(self):
        """Test code runner with correct implementation"""
        from app.services.test_service import TestService
        
        # This would normally be in the frontend, but we're testing the concept
        code = """
        function sumArray(arr) {
            return arr.reduce((a, b) => a + b, 0);
        }
        """
        
        test_cases = [
            {"input": "[1, 2, 3, 4, 5]", "expectedOutput": "15"},
            {"input": "[]", "expectedOutput": "0"},
            {"input": "[10, -5]", "expectedOutput": "5"}
        ]
        
        # This would be implemented in the frontend codeRunner
        # For now, we'll just verify the test case structure
        assert len(test_cases) == 3
        assert all("input" in tc and "expectedOutput" in tc for tc in test_cases)

    def test_test_case_structure(self):
        """Test that test cases have the correct structure"""
        test_cases = [
            {"input": "[1, 2, 3]", "expectedOutput": "6"},
            {"input": "[]", "expectedOutput": "0"}
        ]
        
        for test_case in test_cases:
            assert "input" in test_case
            assert "expectedOutput" in test_case
            assert isinstance(test_case["input"], str)
            assert isinstance(test_case["expectedOutput"], str)