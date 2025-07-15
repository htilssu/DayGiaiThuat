# UserCourseProgress System

## Overview

The `UserCourseProgress` system provides detailed tracking of user progress through individual lessons in courses. This replaces the simple progress tracking with a comprehensive system that tracks viewing history, completion status, and provides rich analytics.

## Database Schema

### UserCourseProgress Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | int (PK) | Primary key |
| `user_course_id` | FK to UserCourse | Links to user's course enrollment |
| `topic_id` | int | Topic ID within the course |
| `lesson_id` | int | Lesson ID within the topic |
| `status` | enum | `not_started`, `in_progress`, `completed` |
| `last_viewed_at` | datetime | When lesson was last viewed (nullable) |
| `completed_at` | datetime | When lesson was completed (nullable) |
| `created_at` | datetime | Record creation time |
| `updated_at` | datetime | Last update time |

### Enhanced UserCourse Table

The `UserCourse` table now includes cached fields for performance:
- `current_topic`: Currently active topic (cached)
- `current_lesson`: Currently active lesson (cached)  
- `current_section`: Currently active section (cached)

## Key Features

### 1. Progress Status Tracking
- **NOT_STARTED**: User hasn't opened the lesson yet
- **IN_PROGRESS**: User has viewed but not completed the lesson
- **COMPLETED**: User has finished the lesson

### 2. Timestamp Tracking
- `last_viewed_at`: Records when user last accessed the lesson
- `completed_at`: Records when user completed the lesson

### 3. Rich Analytics
- Course completion percentage
- Lesson-by-lesson progress tracking
- Learning pattern analysis
- Time spent tracking

## API Endpoints

### Progress Management

#### Create Progress Record
```http
POST /progress/
Content-Type: application/json

{
    "user_course_id": 1,
    "topic_id": 1,
    "lesson_id": 1,
    "status": "not_started"
}
```

#### Get Lesson Progress
```http
GET /progress/{user_course_id}/{topic_id}/{lesson_id}
```

#### Update Lesson Progress
```http
PUT /progress/{user_course_id}/{topic_id}/{lesson_id}
Content-Type: application/json

{
    "status": "in_progress",
    "last_viewed_at": "2025-07-14T10:30:00Z"
}
```

#### Mark Lesson as Viewed
```http
POST /progress/{user_course_id}/{topic_id}/{lesson_id}/view
```

#### Mark Lesson as Completed
```http
POST /progress/{user_course_id}/{topic_id}/{lesson_id}/complete
```

### Analytics & Reporting

#### Get Course Progress Summary
```http
GET /progress/course/{user_course_id}/summary
```

Response:
```json
{
    "user_course_id": 1,
    "total_lessons": 20,
    "completed_lessons": 15,
    "in_progress_lessons": 3,
    "not_started_lessons": 2,
    "completion_percentage": 75.0,
    "current_topic_id": 3,
    "current_lesson_id": 8,
    "last_activity_at": "2025-07-14T10:30:00Z"
}
```

#### Get Topic Progress
```http
GET /progress/course/{user_course_id}/topic/{topic_id}
```

#### Get All Course Progress
```http
GET /progress/course/{user_course_id}
```

## Usage Examples

### Service Layer
```python
from app.services.user_course_progress_service import UserCourseProgressService

# Mark lesson as viewed
await progress_service.mark_lesson_viewed(
    user_course_id=1,
    topic_id=1, 
    lesson_id=1
)

# Get progress summary
summary = await progress_service.get_user_course_progress_summary(
    user_course_id=1
)
```

### Direct Database Operations
```python
from app.models.user_course_progress_model import UserCourseProgress, ProgressStatus

# Create new progress record
progress = UserCourseProgress(
    user_course_id=1,
    topic_id=1,
    lesson_id=1,
    status=ProgressStatus.NOT_STARTED
)
```

## Benefits

### 🎯 Detailed Tracking
- Know exactly which lessons users have viewed vs completed
- Track learning patterns and time spent
- Identify where users get stuck

### 📊 Rich Analytics
- Calculate accurate completion percentages
- Generate detailed progress reports
- Track learning velocity

### ⚡ Performance Optimized
- Cached current position in UserCourse table
- Indexed fields for efficient queries
- Optimized for read-heavy workloads

### 🔗 Relationship Management
- Cascade delete ensures data consistency
- Links to existing UserCourse records
- Maintains referential integrity

### 📈 Scalable Design
- Supports multiple course enrollments per user
- Easy to extend with additional metrics
- Compatible with existing course structure

## Migration

The new system has been added via Alembic migration `b32e785910da_add_user_course_progress_table`. 

To apply:
```bash
alembic upgrade head
```

## Performance Considerations

### Caching Strategy
- Current topic/lesson cached in `UserCourse` for quick access
- Avoid JOIN queries for common operations
- Use indexed fields for filtering

### Query Optimization
- Index on `user_course_id`, `topic_id`, `lesson_id`
- Index on `status` for filtering by progress state
- Index on `created_at` for time-based queries

## Future Enhancements

Potential extensions to the system:
- Time spent per lesson tracking
- Lesson attempt history
- Difficulty ratings per lesson
- Learning path recommendations
- Gamification elements (streaks, achievements)
