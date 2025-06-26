from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.course_model import Course
from app.schemas.course_schema import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)
from app.schemas.user_profile_schema import UserExcludeSecret
from app.core.agents.input_test_agent import InputTestAgent, get_input_test_agent
from app.utils.utils import get_current_user

router = APIRouter(
    prefix="/admin/courses",
    tags=["admin-courses"],
    responses={404: {"description": "Không tìm thấy khóa học"}},
)


def get_admin_user(current_user: UserExcludeSecret = Depends(get_current_user)):
    """Kiểm tra quyền admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này",
        )
    return current_user


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo khóa học mới (Admin)",
    responses={
        201: {"description": "Created"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Tạo một khóa học mới (chỉ admin)

    Args:
        course_data: Dữ liệu để tạo khóa học
        db: Session database
        admin_user: Thông tin admin đã xác thực

    Returns:
        CourseResponse: Thông tin của khóa học vừa tạo

    Raises:
        HTTPException: Nếu có lỗi khi tạo khóa học
    """
    try:
        # Tạo đối tượng Course từ dữ liệu đầu vào
        new_course = Course(**course_data.dict())

        # Thêm vào database
        db.add(new_course)
        db.commit()
        db.refresh(new_course)

        # Tạo bài test đầu vào async
        from app.services.course_service import CourseService

        course_service = CourseService(db)
        await course_service.generate_input_test_async(new_course.id)

        return new_course
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo khóa học: {str(e)}",
        )


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Cập nhật khóa học (Admin)",
    responses={
        200: {"description": "OK"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
        500: {"description": "Internal server error"},
    },
)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Cập nhật thông tin khóa học (chỉ admin)

    Args:
        course_id: ID của khóa học cần cập nhật
        course_data: Dữ liệu cập nhật
        db: Session database
        admin_user: Thông tin admin đã xác thực

    Returns:
        CourseResponse: Thông tin khóa học sau khi cập nhật

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc có lỗi khi cập nhật
    """
    # Tìm khóa học cần cập nhật
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    try:
        # Cập nhật các field được gửi lên
        update_data = course_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        # Lưu thay đổi
        db.commit()
        db.refresh(course)

        return course
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật khóa học: {str(e)}",
        )


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa khóa học (Admin)",
    responses={
        204: {"description": "Xóa thành công"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
        500: {"description": "Internal server error"},
    },
)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Xóa khóa học (chỉ admin)

    Args:
        course_id: ID của khóa học cần xóa
        db: Session database
        admin_user: Thông tin admin đã xác thực

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc có lỗi khi xóa
    """
    # Tìm khóa học cần xóa
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    try:
        # Xóa khóa học
        db.delete(course)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa khóa học: {str(e)}",
        )


@router.post(
    "/{course_id}/test",
    summary="Tạo bài kiểm tra đầu vào cho khóa học (Admin)",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Created"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def create_test(
    course_id: int,
    input_test_agent: InputTestAgent = Depends(get_input_test_agent),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Tạo bài kiểm tra đầu vào cho khóa học (chỉ admin)
    """
    return await input_test_agent.act(course_id=course_id)


@router.get(
    "",
    summary="Lấy tất cả khóa học (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
    },
)
async def get_all_courses_admin(
    db: Session = Depends(get_db),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Lấy tất cả khóa học bao gồm cả chưa được published (chỉ admin)
    """
    courses = db.query(Course).order_by(Course.created_at.desc()).all()
    return courses


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Lấy chi tiết khóa học (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
    },
)
async def get_course_by_id_admin(
    course_id: int,
    db: Session = Depends(get_db),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Lấy thông tin chi tiết của một khóa học (chỉ admin, bao gồm cả chưa published)
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    return course
