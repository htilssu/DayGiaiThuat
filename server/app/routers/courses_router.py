from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.course_model import Course
from app.schemas.course_schema import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
    CourseListResponse,
)

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    responses={404: {"description": "Không tìm thấy khóa học"}},
)


@router.get("", response_model=CourseListResponse)
async def get_courses(
    page: int = Query(1, gt=0, description="Số trang"),
    limit: int = Query(10, gt=0, le=100, description="Số item mỗi trang"),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách khóa học với phân trang

    Args:
        page: Số trang, bắt đầu từ 1
        limit: Số lượng item mỗi trang
        db: Session database

    Returns:
        CourseListResponse: Danh sách khóa học và thông tin phân trang
    """
    # Tính toán offset
    offset = (page - 1) * limit

    # Truy vấn khóa học
    total_courses = db.query(Course).count()
    courses = (
        db.query(Course)
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


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    """
    Lấy thông tin chi tiết của một khóa học

    Args:
        course_id: ID của khóa học
        db: Session database

    Returns:
        CourseResponse: Thông tin chi tiết của khóa học

    Raises:
        HTTPException: Nếu không tìm thấy khóa học
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )
    return course


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(course_data: CourseCreate, db: Session = Depends(get_db)):
    """
    Tạo một khóa học mới

    Args:
        course_data: Dữ liệu để tạo khóa học
        db: Session database

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

        return new_course
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo khóa học: {str(e)}",
        )


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int, course_data: CourseUpdate, db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin một khóa học

    Args:
        course_id: ID của khóa học cần cập nhật
        course_data: Dữ liệu cập nhật
        db: Session database

    Returns:
        CourseResponse: Thông tin khóa học sau khi cập nhật

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc có lỗi khi cập nhật
    """
    try:
        # Tìm khóa học cần cập nhật
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )

        # Cập nhật thông tin khóa học từ dữ liệu đầu vào
        course_dict = course_data.dict(exclude_unset=True)
        for key, value in course_dict.items():
            setattr(course, key, value)

        # Lưu thay đổi vào database
        db.commit()
        db.refresh(course)

        return course
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật khóa học: {str(e)}",
        )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    Xóa một khóa học

    Args:
        course_id: ID của khóa học cần xóa
        db: Session database

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc có lỗi khi xóa
    """
    try:
        # Tìm khóa học cần xóa
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )

        # Xóa khóa học
        db.delete(course)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa khóa học: {str(e)}",
        )
