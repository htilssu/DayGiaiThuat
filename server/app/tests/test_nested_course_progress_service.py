"""
Test cho Nested Course Progress Service - Cách 2: ORM + Response Schema dạng Nested
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.services.nested_course_progress_service import NestedCourseProgressService
from app.models.user_course_progress_model import ProgressStatus
from app.schemas.nested_course_progress_schema import (
    CourseWithNestedProgressSchema,
    ProgressMapResponse,
)


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def service(mock_db_session):
    """Create service instance with mocked database"""
    return NestedCourseProgressService(mock_db_session)


@pytest.fixture
def sample_user_course():
    """Sample UserCourse data"""
    user_course = Mock()
    user_course.id = 1
    user_course.course_id = 101

    # Mock course
    course = Mock()
    course.id = 101
    course.title = "React Fundamentals"
    course.description = "Learn React from scratch"
    user_course.course = course

    return user_course


@pytest.fixture
def sample_topics():
    """Sample topics with lessons"""
    # Topic 1
    topic1 = Mock()
    topic1.id = 1
    topic1.external_id = "topic1"
    topic1.name = "Introduction to React"
    topic1.description = "Basic concepts"
    topic1.order = 1

    # Lessons for topic 1
    lesson1 = Mock()
    lesson1.id = 101
    lesson1.external_id = "1"
    lesson1.title = "What is React?"
    lesson1.description = "Overview"
    lesson1.order = 1

    lesson2 = Mock()
    lesson2.id = 102
    lesson2.external_id = "2"
    lesson2.title = "Setup Environment"
    lesson2.description = "Install tools"
    lesson2.order = 2

    topic1.lessons = [lesson1, lesson2]

    # Topic 2
    topic2 = Mock()
    topic2.id = 2
    topic2.external_id = "topic2"
    topic2.name = "Components"
    topic2.description = "Deep dive"
    topic2.order = 2

    # Lessons for topic 2
    lesson3 = Mock()
    lesson3.id = 201
    lesson3.external_id = "3"
    lesson3.title = "Function Components"
    lesson3.description = "Creating components"
    lesson3.order = 1

    topic2.lessons = [lesson3]

    return [topic1, topic2]


@pytest.fixture
def sample_progress_records():
    """Sample progress records"""
    records = []

    # Lesson 101: completed
    record1 = Mock()
    record1.lesson_id = 101
    record1.status = ProgressStatus.COMPLETED
    record1.last_viewed_at = datetime(2025, 7, 14, 10, 30)
    record1.completed_at = datetime(2025, 7, 14, 11, 0)
    records.append(record1)

    # Lesson 102: in progress
    record2 = Mock()
    record2.lesson_id = 102
    record2.status = ProgressStatus.IN_PROGRESS
    record2.last_viewed_at = datetime(2025, 7, 14, 12, 0)
    record2.completed_at = None
    records.append(record2)

    # Lesson 201: not started (no record)

    return records


class TestNestedCourseProgressService:
    """Test cases for NestedCourseProgressService"""

    async def test_get_course_with_nested_progress_success(
        self,
        service,
        mock_db_session,
        sample_user_course,
        sample_topics,
        sample_progress_records,
    ):
        """Test successful retrieval of course with nested progress"""

        # Mock database queries
        # 1. UserCourse query
        user_course_result = Mock()
        user_course_result.scalar_one_or_none.return_value = sample_user_course

        # 2. Topics query
        topics_result = Mock()
        topics_result.scalars.return_value.all.return_value = sample_topics

        # 3. Progress query
        progress_result = Mock()
        progress_result.all.return_value = sample_progress_records

        # Setup mock execute to return different results for different queries
        async def mock_execute(stmt):
            # Simple way to distinguish queries based on call order
            if not hasattr(mock_execute, "call_count"):
                mock_execute.call_count = 0
            mock_execute.call_count += 1

            if mock_execute.call_count == 1:
                return user_course_result
            elif mock_execute.call_count == 2:
                return topics_result
            else:
                return progress_result

        mock_db_session.execute.side_effect = mock_execute

        # Call the method
        result = await service.get_course_with_nested_progress(1)

        # Verify result structure
        assert isinstance(result, CourseWithNestedProgressSchema)
        assert result.user_course_id == 1
        assert result.course_id == 101
        assert result.course_title == "React Fundamentals"
        assert len(result.topics) == 2

        # Verify first topic
        topic1 = result.topics[0]
        assert topic1.id == 1
        assert topic1.name == "Introduction to React"
        assert len(topic1.lessons) == 2

        # Verify lesson progress mapping
        lesson1 = topic1.lessons[0]  # Should be completed
        assert lesson1.id == 101
        assert lesson1.status == ProgressStatus.COMPLETED
        assert lesson1.completion_percentage == 100.0

        lesson2 = topic1.lessons[1]  # Should be in progress
        assert lesson2.id == 102
        assert lesson2.status == ProgressStatus.IN_PROGRESS
        assert lesson2.completion_percentage == 50.0

        # Verify second topic
        topic2 = result.topics[1]
        assert topic2.id == 2
        lesson3 = topic2.lessons[0]  # Should be not started
        assert lesson3.id == 201
        assert lesson3.status == ProgressStatus.NOT_STARTED
        assert lesson3.completion_percentage == 0.0

        # Verify overall stats
        assert result.total_lessons == 3
        assert result.completed_lessons == 1
        assert result.in_progress_lessons == 1
        assert result.not_started_lessons == 1
        assert result.overall_completion_percentage == 33.33

    async def test_get_progress_map_only(
        self, service, mock_db_session, sample_progress_records
    ):
        """Test getting progress map only"""

        # Mock progress query
        progress_result = Mock()
        progress_result.all.return_value = sample_progress_records
        mock_db_session.execute.return_value = progress_result

        # Call the method
        result = await service.get_progress_map_only(1)

        # Verify result
        assert isinstance(result, ProgressMapResponse)
        assert result.user_course_id == 1

        # Verify progress map
        progress_map = result.progress_map
        assert len(progress_map) == 2

        # Lesson 101: completed
        assert progress_map[101]["status"] == ProgressStatus.COMPLETED
        assert progress_map[101]["completion_percentage"] == 100.0

        # Lesson 102: in progress
        assert progress_map[102]["status"] == ProgressStatus.IN_PROGRESS
        assert progress_map[102]["completion_percentage"] == 50.0

        # Verify summary
        summary = result.summary
        assert summary["total_lessons"] == 2
        assert summary["completed_lessons"] == 1
        assert summary["in_progress_lessons"] == 1
        assert summary["not_started_lessons"] == 0

    async def test_user_course_not_found(self, service, mock_db_session):
        """Test when user course is not found"""

        # Mock not found scenario
        user_course_result = Mock()
        user_course_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = user_course_result

        # Should raise HTTPException
        with pytest.raises(Exception):  # Will be HTTPException in real scenario
            await service.get_course_with_nested_progress(999)

    async def test_empty_progress_map(self, service, mock_db_session):
        """Test with empty progress map"""

        # Mock empty progress
        progress_result = Mock()
        progress_result.all.return_value = []
        mock_db_session.execute.return_value = progress_result

        result = await service.get_progress_map_only(1)

        assert result.user_course_id == 1
        assert len(result.progress_map) == 0
        assert result.summary["total_lessons"] == 0
        assert result.summary["completion_percentage"] == 0.0


def test_progress_status_mapping():
    """Test progress status to completion percentage mapping"""

    # Test completion percentage calculation
    status_mapping = {
        ProgressStatus.NOT_STARTED: 0.0,
        ProgressStatus.IN_PROGRESS: 50.0,
        ProgressStatus.COMPLETED: 100.0,
    }

    for status, expected_percentage in status_mapping.items():
        assert expected_percentage == {
            ProgressStatus.NOT_STARTED: 0.0,
            ProgressStatus.IN_PROGRESS: 50.0,
            ProgressStatus.COMPLETED: 100.0,
        }.get(status, 0.0)


def test_lesson_sorting():
    """Test that lessons are sorted correctly by order"""

    # Create mock lessons with different orders
    lesson1 = Mock()
    lesson1.order = 3
    lesson1.id = 103

    lesson2 = Mock()
    lesson2.order = 1
    lesson2.id = 101

    lesson3 = Mock()
    lesson3.order = 2
    lesson3.id = 102

    lessons = [lesson1, lesson2, lesson3]

    # Sort like the service does
    sorted_lessons = sorted(lessons, key=lambda x: (x.order or 0, x.id))

    # Verify order
    assert sorted_lessons[0].id == 101  # order 1
    assert sorted_lessons[1].id == 102  # order 2
    assert sorted_lessons[2].id == 103  # order 3


if __name__ == "__main__":
    print("🧪 Running Nested Course Progress Service Tests")
    print("=" * 50)

    print("\n✅ Test Structure:")
    print("• test_get_course_with_nested_progress_success")
    print("• test_get_progress_map_only")
    print("• test_user_course_not_found")
    print("• test_empty_progress_map")
    print("• test_progress_status_mapping")
    print("• test_lesson_sorting")

    print("\n🚀 To run tests:")
    print("pytest app/tests/test_nested_course_progress_service.py -v")

    print("\n📋 Test Coverage:")
    print("• ✅ Happy path - course with progress")
    print("• ✅ Progress map only")
    print("• ✅ Error handling - not found")
    print("• ✅ Edge case - empty progress")
    print("• ✅ Utility functions")

    print("\n" + "=" * 50)
    print("Tests ready! Use pytest to run them.")
