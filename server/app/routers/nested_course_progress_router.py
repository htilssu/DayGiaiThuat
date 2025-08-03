"""
Router cho Nested Course Progress - Cách 2: ORM + Response Schema dạng Nested
"""

from fastapi import APIRouter, Depends

from app.utils.utils import get_current_user_optional
from app.models.user_model import User
from app.schemas.nested_course_progress_schema import (
    CourseWithNestedProgressSchema,
    TopicWithProgressSchema,
    ProgressMapResponse,
)
from app.services.nested_course_progress_service import (
    NestedCourseProgressService,
    get_nested_course_progress_service,
)

router = APIRouter()


@router.get(
    "/nested/course/{user_course_id}",
    response_model=CourseWithNestedProgressSchema,
    summary="Get course with nested topics, lessons and progress",
    description="""
    Cách 2: ORM + Response Schema dạng Nested
    
    Lấy toàn bộ course với topics và lessons nested, bao gồm progress status.
    
    **Cách hoạt động:**
    1. Query UserCourse với course info
    2. Query tất cả topics với lessons (eager loading)
    3. Query progress map riêng biệt: `lesson_id -> {status, last_viewed_at, completed_at}`
    4. Map progress status cho từng lesson bằng Python
    
    **Ưu điểm:**
    - Tránh JOIN phức tạp
    - Performance tốt với khóa học nhỏ/vừa
    - Dễ cache và optimize
    - Response nested đẹp, dễ sử dụng
    
    **Response format:**
    ```json
    {
        "user_course_id": 1,
        "course_title": "React Fundamentals",
        "topics": [
            {
                "id": 1,
                "name": "Introduction",
                "lessons": [
                    {
                        "id": 101,
                        "title": "Getting Started",
                        "status": "completed",
                        "completion_percentage": 100.0
                    },
                    {
                        "id": 102,
                        "title": "Components",
                        "status": "in_progress",
                        "completion_percentage": 50.0
                    }
                ],
                "topic_completion_percentage": 75.0
            }
        ],
        "overall_completion_percentage": 45.0
    }
    ```
    """,
)
async def get_course_with_nested_progress(
    user_course_id: int,
    current_user: User = Depends(get_current_user_optional),
    service: NestedCourseProgressService = Depends(get_nested_course_progress_service),
):
    """
    Lấy course với topics, lessons và progress nested (Cách 2)
    """
    return await service.get_course_with_nested_progress(user_course_id)


@router.get(
    "/nested/course/{user_course_id}/topic/{topic_id}",
    response_model=TopicWithProgressSchema,
    summary="Get single topic with nested lessons and progress",
    description="""
    Lấy một topic cụ thể với lessons và progress nested.
    
    Tương tự endpoint trên nhưng chỉ trả về 1 topic để optimize performance
    khi frontend chỉ cần load 1 topic.
    """,
)
async def get_topic_with_nested_progress(
    user_course_id: int,
    topic_id: int,
    current_user: User = Depends(get_current_user_optional),
    service: NestedCourseProgressService = Depends(get_nested_course_progress_service),
):
    """
    Lấy một topic với lessons và progress nested
    """
    return await service.get_topic_with_nested_progress(user_course_id, topic_id)


@router.get(
    "/nested/course/{user_course_id}/progress-map",
    response_model=ProgressMapResponse,
    summary="Get lesson progress map only",
    description="""
    Chỉ lấy progress map mà không cần nested data.
    
    **Use case:**
    - Frontend muốn tự map progress
    - Check nhanh progress status
    - Optimize performance khi chỉ cần progress info
    
    **Response format:**
    ```json
    {
        "user_course_id": 1,
        "progress_map": {
            "101": {
                "status": "completed",
                "last_viewed_at": "2025-07-14T10:30:00Z",
                "completed_at": "2025-07-14T11:00:00Z",
                "completion_percentage": 100.0
            },
            "102": {
                "status": "in_progress",
                "last_viewed_at": "2025-07-14T12:00:00Z",
                "completed_at": null,
                "completion_percentage": 50.0
            }
        },
        "summary": {
            "total_lessons": 20,
            "completed_lessons": 15,
            "completion_percentage": 75.0
        }
    }
    ```
    """,
)
async def get_progress_map_only(
    user_course_id: int,
    current_user: User = Depends(get_current_user_optional),
    service: NestedCourseProgressService = Depends(get_nested_course_progress_service),
):
    """
    Chỉ lấy progress map mà không cần nested data
    """
    return await service.get_progress_map_only(user_course_id)
