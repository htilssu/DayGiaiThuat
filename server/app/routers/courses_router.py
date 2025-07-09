from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query, status, Body
from sqlalchemy.orm import Session, joinedload

from app.database.database import get_db
from app.models.course_model import Course
from app.models.topic_model import Topic
from app.schemas.course_schema import (
    CourseListResponse,
    CourseDetailResponse,
    rebuild_course_models,
)
from app.schemas.topic_schema import (
    TopicWithUserState,
    TopicWithLessonsResponse,
)
from app.schemas.lesson_schema import (
    LessonResponseSchema,
)
from app.schemas.user_course_schema import (
    CourseEnrollmentResponse,
)
from app.schemas.test_schema import TestRead, TestSessionRead
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.course_service import CourseService, get_course_service
from app.services.topic_service import TopicService, get_topic_service
from app.services.test_service import TestService, get_test_service
from app.utils.utils import get_current_user, get_current_user_optional
from app.utils.model_utils import convert_lesson_to_schema


router = APIRouter(
    prefix="/courses",
    tags=["Khóa học"],
    responses={404: {"description": "Không tìm thấy khóa học"}},
)

# Rebuild models để resolve forward references
rebuild_course_models()


@router.get("", response_model=CourseListResponse)
async def get_courses(
    page: int = Query(1, gt=0, description="Số trang"),
    limit: int = Query(10, gt=0, le=100, description="Số item mỗi trang"),
    db: Session = Depends(get_db),
    current_user: UserExcludeSecret = Depends(get_current_user_optional),
):
    """
    Lấy danh sách khóa học với phân trang (chỉ hiển thị khóa học được công khai)

    Args:
        page: Số trang, bắt đầu từ 1
        limit: Số lượng item mỗi trang
        db: Session database
        current_user: Thông tin người dùng hiện tại (nếu đã đăng nhập)

    Returns:
        CourseListResponse: Danh sách khóa học và thông tin phân trang
    """
    # Tính toán offset
    offset = (page - 1) * limit

    # Chỉ hiển thị khóa học được công khai cho user
    total_courses = db.query(Course).filter(Course.is_published == True).count()
    courses = (
        db.query(Course)
        .filter(Course.is_published == True)
        .order_by(Course.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Tính tổng số trang
    total_pages = (total_courses + limit - 1) // limit

    return {
        "items": courses,
        "total": total_courses,
        "page": page,
        "limit": limit,
        "totalPages": total_pages,
    }


@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    responses={
        200: {"description": "OK"},
        404: {"description": "Không tìm thấy khóa học"},
        403: {"description": "Không có quyền truy cập khóa học"},
    },
)
async def get_course_by_id(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserExcludeSecret = Depends(get_current_user_optional),
    course_service: CourseService = Depends(get_course_service),
):
    """
    Lấy thông tin chi tiết của một khóa học bao gồm topics và lessons

    Args:
        course_id: ID của khóa học
        db: Session database
        current_user: Thông tin người dùng hiện tại (nếu đã đăng nhập)

    Returns:
        CourseDetailResponse: Thông tin chi tiết của khóa học kèm topics và lessons

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc không có quyền truy cập
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    # Kiểm tra quyền truy cập - chỉ khóa học được công khai mới có thể xem (trừ admin)
    if not course.is_published and (not current_user or not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập khóa học này",
        )

    # Kiểm tra trạng thái đăng ký nếu người dùng đã đăng nhập
    is_enrolled = False
    if current_user:
        is_enrolled = course_service.is_enrolled(current_user.id, course_id)

    # Chuyển đổi course ORM sang schema bằng hàm tiện ích
    course_response = convert_course_to_schema(course, is_enrolled)
    return course_response


# Hàm tiện ích chuyển đổi Course ORM sang CourseDetailResponse schema


def convert_course_to_schema(course, is_enrolled=False):
    """
    Chuyển đổi đối tượng Course ORM sang CourseDetailResponse schema, bao gồm cả topics và lessons
    """
    topics = course.topics if hasattr(course, "topics") else []
    topics_response = []
    for topic in topics:
        lessons_response = []
        for lesson in sorted(
            getattr(topic, "lessons", []), key=lambda x: getattr(x, "created_at", 0)
        ):
            lesson_response = convert_lesson_to_schema(lesson)
            lessons_response.append(lesson_response)
        topic_response = TopicWithLessonsResponse(
            id=topic.id,
            external_id=getattr(topic, "external_id", None),
            course_id=topic.course_id,
            name=topic.name,
            description=topic.description,
            prerequisites=getattr(topic, "prerequisites", None),
            created_at=topic.created_at,
            updated_at=topic.updated_at,
            lessons=lessons_response,
        )
        topics_response.append(topic_response)
    test_generation_status = getattr(course, "test_generation_status", None)
    if not isinstance(test_generation_status, str) or not test_generation_status:
        test_generation_status = "NOT_STARTED"
    course_response = CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        thumbnail_url=getattr(course, "thumbnail_url", None),
        level=getattr(course, "level", None),
        duration=getattr(course, "duration", None),
        price=getattr(course, "price", None),
        is_published=getattr(course, "is_published", None),
        tags=getattr(course, "tags", None),
        requirements=getattr(course, "requirements", None),
        what_you_will_learn=getattr(course, "what_you_will_learn", None),
        created_at=course.created_at,
        updated_at=course.updated_at,
        topics=topics_response,
        test_generation_status=test_generation_status,
        is_enrolled=is_enrolled,
    )
    return course_response


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
    current_user=Depends(get_current_user),
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
    result = course_service.enroll_course(current_user.id, course_id)
    return result


@router.delete(
    "/enroll/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Hủy đăng ký thành công"},
        404: {"description": "Không tìm thấy đăng ký khóa học"},
        500: {"description": "Internal server error"},
    },
)
async def unenroll_course(
    course_id: int,
    course_service: CourseService = Depends(get_course_service),
    current_user=Depends(get_current_user),
):
    """
    Hủy đăng ký khóa học

    Args:
        course_id: ID của khóa học
        course_service: Service xử lý khóa học
        current_user: Thông tin người dùng hiện tại

    Raises:
        HTTPException: Nếu có lỗi khi hủy đăng ký
    """
    # Sử dụng service để hủy đăng ký khóa học
    course_service.unenroll_course(current_user.id, course_id)


@router.get(
    "/user/enrolled",
    responses={
        200: {"description": "OK"},
        500: {"description": "Internal server error"},
    },
)
async def get_enrolled_courses(
    course_service: CourseService = Depends(get_course_service),
    current_user=Depends(get_current_user),
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
    enrolled_courses = course_service.get_user_courses(current_user.id)
    return enrolled_courses


@router.get(
    "/{course_id}/check-enrollment",
    responses={
        200: {"description": "OK"},
    },
)
async def check_enrollment(
    course_id: int,
    course_service: CourseService = Depends(get_course_service),
    current_user=Depends(get_current_user),
):
    """
    Kiểm tra trạng thái đăng ký khóa học

    Args:
        course_id: ID của khóa học
        course_service: Service xử lý khóa học
        current_user: Thông tin người dùng hiện tại

    Returns:
        dict: Trạng thái đăng ký
    """
    is_enrolled = course_service.is_enrolled(current_user.id, course_id)
    return {"is_enrolled": is_enrolled}


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
    course = course_service.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )
    topics = course.topics
    if not topics:
        return []
    return topics


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
    entry_test = course_service.get_course_entry_test(course_id)
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
