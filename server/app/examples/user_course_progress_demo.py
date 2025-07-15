"""
Demo script showing how to use the new UserCourseProgress system

This script demonstrates the key features of the UserCourseProgress system:
1. Creating progress records
2. Updating lesson progress
3. Marking lessons as viewed/completed
4. Getting progress summaries
"""

from datetime import datetime
from app.models.user_course_progress_model import ProgressStatus
from app.schemas.user_course_progress_schema import (
    UserCourseProgressCreate,
    UserCourseProgressUpdate,
)


def demo_usage_examples():
    """Examples of how to use the UserCourseProgress system"""

    # Example 1: Create a new progress record
    create_data = UserCourseProgressCreate(
        user_course_id=1, topic_id=1, lesson_id=1, status=ProgressStatus.NOT_STARTED
    )

    # Example 2: Update progress to mark lesson as viewed
    view_update = UserCourseProgressUpdate(
        status=ProgressStatus.IN_PROGRESS, last_viewed_at=datetime.utcnow()
    )

    # Example 3: Mark lesson as completed
    complete_update = UserCourseProgressUpdate(
        status=ProgressStatus.COMPLETED,
        completed_at=datetime.utcnow(),
        last_viewed_at=datetime.utcnow(),
    )

    print("UserCourseProgress Demo Examples:")
    print(f"1. Create data: {create_data}")
    print(f"2. View update: {view_update}")
    print(f"3. Complete update: {complete_update}")


# API Usage Examples:

"""
1. Create progress record:
POST /progress/
{
    "user_course_id": 1,
    "topic_id": 1,
    "lesson_id": 1,
    "status": "not_started"
}

2. Mark lesson as viewed:
POST /progress/1/1/1/view

3. Mark lesson as completed:
POST /progress/1/1/1/complete

4. Get progress for a lesson:
GET /progress/1/1/1

5. Update progress manually:
PUT /progress/1/1/1
{
    "status": "in_progress",
    "last_viewed_at": "2025-07-14T10:30:00Z"
}

6. Get course progress summary:
GET /progress/course/1/summary

7. Get topic lessons progress:
GET /progress/course/1/topic/1

8. Get all course progress:
GET /progress/course/1

9. Delete progress record:
DELETE /progress/1/1/1
"""


# Database Benefits:

"""
Advantages of the new UserCourseProgress system:

✅ Detailed Tracking:
- Track exact progress for each lesson
- Know which lessons user has viewed vs completed
- Timestamp when lessons were last viewed/completed

✅ Flexible Progress States:
- NOT_STARTED: User hasn't opened the lesson yet
- IN_PROGRESS: User has viewed but not completed
- COMPLETED: User has finished the lesson

✅ Performance Optimization:
- Cached current_topic/lesson in UserCourse for quick access
- Indexed fields for efficient queries
- Cascade delete ensures data consistency

✅ Rich Analytics:
- Calculate completion percentages
- Track learning patterns
- Generate progress reports

✅ Scalable Design:
- Supports multiple course enrollments per user
- Easy to extend with additional progress metrics
- Compatible with existing course structure
"""

if __name__ == "__main__":
    demo_usage_examples()
