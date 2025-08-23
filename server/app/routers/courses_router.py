from typing import List
from datetime import datetime

from app.database.database import get_async_db
from app.models.course_model import Course
from app.schemas.course_schema import (
    CourseDetailWithProgressResponse,
    CourseListItem,
    CourseListResponse,
)
from app.schemas.test_schema import TestRead, TestSessionRead
from app.schemas.topic_schema import TopicWithUserState, TopicWithLesson
from app.schemas.user_course_schema import CourseEnrollmentResponse
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.course_service import CourseService, get_course_service, get_course_with_progress
from app.services.test_service import TestService, get_test_service
from app.services.topic_service import TopicService, get_topic_service
from app.utils.utils import get_current_user, get_current_user_optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/courses",
    tags=["Khóa học"],
    responses={404: {"description": "Không tìm thấy khóa học"}},
)


@router.get("/{course_id}/topics")
async def get_course_topics(
        course_id: int,
        topic_service: TopicService = Depends(get_topic_service),
        course_service: CourseService = Depends(get_course_service),
        current_user: UserExcludeSecret = Depends(get_current_user_optional),
):
    topics = await course_service.get_topics(course_id)
    return [TopicWithLesson.model_validate(topic) for topic in topics]


@router.get(
    "",
    response_model=CourseListResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách khóa học",
)
async def get_courses(
        page: int = Query(1, gt=0, description="Số trang"),
        limit: int = Query(10, gt=0, le=100, description="Số item mỗi trang"),
        db: AsyncSession = Depends(get_async_db),
        current_user: UserExcludeSecret = Depends(get_current_user_optional),
        course_service: CourseService = Depends(get_course_service),
):
    offset = (page - 1) * limit

    result = await db.execute(
        select(Course)
        .filter(Course.is_published == True)
        .order_by(Course.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    courses = result.scalars().all()
    if current_user:
        enrolled_courses = await course_service.get_user_courses(current_user.id)
    else:
        enrolled_courses = []

    course_items = []
    for course in courses:
        is_enrolled = False
        if course.id in [enrolled_course.id for enrolled_course in enrolled_courses]:
            is_enrolled = True

        course_item = CourseListItem(
            id=course.id,
            title=course.title,
            description=course.description,
            thumbnail_url=course.thumbnail_url,
            level=course.level,
            duration=course.duration,
            price=course.price,
            tags=course.tags,
            created_at=course.created_at,
            updated_at=course.updated_at,
            is_enrolled=is_enrolled,
        )
        course_items.append(course_item)
    course_total = len(courses)
    total_pages = (course_total + limit - 1) // limit

    return CourseListResponse(
        items=course_items,
        total=course_total,
        page=page,
        limit=limit,
        totalPages=total_pages,
    )


@router.get(
    "/enrolled",
    responses={
        200: {"description": "OK"},
        500: {"description": "Internal server error"},
    },
)
async def get_enrolled_courses(
        course_service: CourseService = Depends(get_course_service),
        current_user: UserExcludeSecret = Depends(get_current_user),
):
    enrolled_courses = await course_service.get_user_courses(current_user.id)
    return enrolled_courses


@router.get(
    "/{course_id}",
    responses={
        200: {"description": "OK"},
        404: {"description": "Không tìm thấy khóa học"},
        403: {"description": "Không có quyền truy cập khóa học"},
    },
)
async def get_course_by_id(
        course_id: int,
        current_user: UserExcludeSecret = Depends(get_current_user_optional),
):
    course = await get_course_with_progress(course_id, current_user.id)
    return course


@router.post(
    "/enroll",
    response_model=CourseEnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Đăng ký thành công"},
        400: {"description": "Dữ liệu không hợp lệ hoặc đã đăng ký"},
        404: {"description": "Không tìm thấy khóa học hoặc người dùng"},
        500: {"description": "Internal server error"},
    },
)
async def enroll_course(
        data: dict = Body(...),
        course_service: CourseService = Depends(get_course_service),
        current_user: UserExcludeSecret = Depends(get_current_user),
):
    course_id = data.get("course_id")
    if not course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="courseId là bắt buộc",
        )

    result = await course_service.enroll_course(current_user.id, course_id)
    return result


@router.get(
    "/{course_id}/user-topics",
    response_model=List[TopicWithUserState],
    summary="Lấy danh sách topic của khóa học theo người dùng",
)
async def get_user_topics(
        course_id: int,
        topic_service: TopicService = Depends(get_topic_service),
        course_service: CourseService = Depends(get_course_service),
        current_user: UserExcludeSecret = Depends(get_current_user),
):
    course = await course_service.get_course(course_id, current_user.id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    topics = await topic_service.get_topics_by_course_id(course_id)
    if not topics:
        return []

    result = []
    for topic in topics:
        result.append(
            TopicWithUserState(
                id=topic.id,
                name=topic.name,
                description=topic.description,
                course_id=topic.course_id,
                user_topic_state=None,  # TODO: implement user topic state logic if needed
            )
        )

    return result


@router.get(
    "/{course_id}/entry-test",
    response_model=TestRead,
    responses={
        200: {"description": "OK"},
        404: {"description": "Không tìm thấy test đầu vào"},
        403: {"description": "Chưa đăng ký khóa học"},
    },
)
async def get_course_entry_test(
        course_id: int,
        course_service: CourseService = Depends(get_course_service),
        current_user: UserExcludeSecret = Depends(get_current_user),
):
    if not course_service.is_enrolled(current_user.id, course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học trước khi làm test đầu vào",
        )

    # Lấy test đầu vào
    entry_test = await course_service.get_course_entry_test(course_id)
    if not entry_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học này không có test đầu vào",
        )

    return entry_test


@router.post(
    "/{course_id}/entry-test/start",
    response_model=TestSessionRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Tạo phiên làm bài test thành công"},
        400: {"description": "Dữ liệu không hợp lệ hoặc đã có phiên làm bài khác"},
        403: {"description": "Chưa đăng ký khóa học"},
        404: {"description": "Không tìm thấy test đầu vào"},
    },
)
async def start_course_entry_test(
        course_id: int,
        course_service: CourseService = Depends(get_course_service),
        test_service: TestService = Depends(get_test_service),
        current_user: UserExcludeSecret = Depends(get_current_user),
):
    if not course_service.is_enrolled(current_user.id, course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học trước khi làm bài test",
        )

    test_session = await test_service.create_test_session_from_course_entry_test(
        course_id=course_id, user_id=current_user.id
    )

    return test_session


@router.post(
    "/{course_id}/complete",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Khóa học được đánh dấu hoàn thành"},
        403: {"description": "Chưa đăng ký khóa học hoặc chưa đạt yêu cầu"},
        404: {"description": "Không tìm thấy khóa học"},
    },
)
async def mark_course_completed(
    course_id: int,
    test_session_id: str = Body(..., description="ID của phiên test đã vượt qua"),
    course_service: CourseService = Depends(get_course_service),
    test_service: TestService = Depends(get_test_service),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Đánh dấu khóa học hoàn thành dựa trên việc vượt qua test
    
    Args:
        course_id: ID của khóa học
        test_session_id: ID của phiên test đã vượt qua
        course_service: Service xử lý khóa học
        test_service: Service xử lý test
        current_user: Thông tin người dùng hiện tại
        
    Returns:
        dict: Thông báo kết quả
        
    Raises:
        HTTPException: Nếu có lỗi khi đánh dấu hoàn thành
    """
    # Kiểm tra người dùng đã đăng ký khóa học chưa
    if not await course_service.is_enrolled(current_user.id, course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học trước",
        )
    
    # Kiểm tra test session có thuộc về user không
    test_session = await test_service.get_test_session(test_session_id)
    if not test_session or test_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Phiên test không hợp lệ hoặc không thuộc về bạn",
        )
    
    # Kiểm tra test session đã hoàn thành và đạt yêu cầu chưa
    if not test_session.is_submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test chưa được hoàn thành",
        )
    
    # Lấy thông tin test để kiểm tra passing score
    test = await test_service.get_test(test_session.test_id)
    if not test or test.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test không thuộc về khóa học này",
        )
    
    # Kiểm tra điểm có đạt yêu cầu không
    if test.passing_score:
        score_percentage = (test_session.score / len(test.questions)) * 100 if test.questions else 0
        if score_percentage < test.passing_score:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Điểm số chưa đạt yêu cầu. Cần tối thiểu {test.passing_score}%",
            )
    
    # Đánh dấu khóa học hoàn thành (có thể implement trong course_service)
    # Tạm thời trả về thành công
    return {
        "message": "Khóa học đã được đánh dấu hoàn thành",
        "course_id": course_id,
        "completed_at": datetime.utcnow().isoformat(),
        "test_session_id": test_session_id,
        "score": test_session.score,
    }
