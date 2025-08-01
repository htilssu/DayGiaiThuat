from typing import List

from app.database.database import get_async_db
from app.models.course_model import Course
from app.schemas.course_schema import (
    CourseDetailWithProgressResponse,
    CourseListItem,
    CourseListResponse,
)
from app.schemas.test_schema import TestRead, TestSessionRead
from app.schemas.topic_schema import TopicWithUserState
from app.schemas.user_course_schema import CourseEnrollmentResponse
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.course_service import CourseService, get_course_service
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
    """
    Lấy danh sách khóa học với phân trang (chỉ hiển thị khóa học được công khai)

    Args:
        page: Số trang, bắt đầu từ 1
        limit: Số lượng item mỗi trang
        db: Session database
        current_user: Thông tin người dùng hiện tại (nếu đã đăng nhập)
        course_service: Service để xử lý logic course

    Returns:
        CourseListResponse: Danh sách khóa học cơ bản và thông tin phân trang
    """
    # Tính toán offset
    offset = (page - 1) * limit

    # Chỉ hiển thị khóa học được công khai cho user
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

    # Chuyển đổi Course thành CourseListItem và kiểm tra trạng thái enrolled
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
    # Tính tổng số trang
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
    """
    Lấy danh sách khóa học đã đăng ký của người dùng hiện tại

    Args:
        course_service: Service xử lý khóa học
        current_user: Thông tin người dùng hiện tại

    Returns:
        List: Danh sách khóa học đã đăng ký
    """
    # Sử dụng service để lấy danh sách khóa học đã đăng ký
    enrolled_courses = await course_service.get_user_courses(current_user.id)
    return enrolled_courses


@router.get(
    "/{course_id}",
    response_model=CourseDetailWithProgressResponse,
    responses={
        200: {"description": "OK"},
        404: {"description": "Không tìm thấy khóa học"},
        403: {"description": "Không có quyền truy cập khóa học"},
    },
)
async def get_course_by_id(
    course_id: int,
    current_user: UserExcludeSecret = Depends(get_current_user_optional),
    course_service: CourseService = Depends(get_course_service),
):
    """
    Lấy thông tin chi tiết của một khóa học bao gồm topics, lessons và progress

    Args:
        course_id: ID của khóa học
        current_user: Thông tin người dùng hiện tại (nếu đã đăng nhập)
        enhanced_service: Enhanced service với progress support

    Returns:
        CourseDetailWithProgressResponse: Thông tin chi tiết của khóa học kèm topics, lessons và progress

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc không có quyền truy cập
    """
    user_id = current_user.id if current_user else None
    course = await course_service.get_course_with_progress(course_id, user_id)
    return course


# Hàm tiện ích chuyển đổi Course ORM sang CourseDetailResponse schema


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
    """
    Đăng ký khóa học

    Args:
        data: Dữ liệu chứa courseId
        course_service: Service xử lý khóa học
        current_user: Thông tin người dùng hiện tại

    Returns:
        CourseEnrollmentResponse: Thông tin đăng ký khóa học và test đầu vào

    Raises:
        HTTPException: Nếu có lỗi khi đăng ký
    """
    course_id = data.get("course_id")
    if not course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="courseId là bắt buộc",
        )

    # Sử dụng service để đăng ký khóa học
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
    """
    Lấy danh sách các topic của khóa học kèm theo trạng thái hoàn thành của người dùng

    Args:
        course_id: ID của khóa học
        topic_service: Service xử lý topic
        current_user: Thông tin người dùng hiện tại

    Returns:
        List[TopicWithUserState]: Danh sách topic kèm trạng thái
    """
    # Kiểm tra khóa học có tồn tại không
    course = await course_service.get_course(course_id, current_user.id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    # Sử dụng topic_service để lấy topics theo course_id thay vì từ course.topics
    topics = await topic_service.get_topics_by_course_id(course_id)
    if not topics:
        return []

    # Chuyển đổi từ TopicResponse sang TopicWithUserState
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
    """
    Lấy test đầu vào của khóa học

    Args:
        course_id: ID của khóa học
        course_service: Service xử lý khóa học
        current_user: Thông tin người dùng hiện tại

    Returns:
        TestRead: Thông tin test đầu vào

    Raises:
        HTTPException: Nếu không tìm thấy test hoặc chưa đăng ký khóa học
    """
    # Kiểm tra xem người dùng đã đăng ký khóa học chưa
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
    """
    Bắt đầu làm bài test đầu vào của khóa học

    Args:
        course_id: ID của khóa học
        course_service: Service xử lý khóa học
        test_service: Service xử lý test
        current_user: Thông tin người dùng hiện tại

    Returns:
        TestSessionRead: Thông tin phiên làm bài test

    Raises:
        HTTPException: Nếu có lỗi khi tạo phiên làm bài
    """
    # Kiểm tra người dùng đã đăng ký khóa học chưa
    if not course_service.is_enrolled(current_user.id, course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học trước khi làm bài test",
        )

    # Tạo test session cho entry test
    test_session = await test_service.create_test_session_from_course_entry_test(
        course_id=course_id, user_id=current_user.id
    )

    return test_session
