from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.storage_service import StorageService, get_storage_service
from app.utils.utils import get_current_user
from app.schemas.user_profile_schema import UserExcludeSecret
from app.models.course_model import Course
from app.database.database import get_db

router = APIRouter(
    prefix="/admin/upload",
    tags=["admin-upload"],
    responses={404: {"description": "Not found"}},
)


class FileUploadResponse(BaseModel):
    key: str
    url: str
    content_type: str
    size: int


def get_admin_user(current_user: UserExcludeSecret = Depends(get_current_user)):
    """Kiểm tra quyền admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này",
        )
    return current_user


@router.post(
    "/course-image/{course_id}",
    response_model=FileUploadResponse,
    summary="Upload ảnh khóa học (Admin)",
    responses={
        200: {"description": "Upload thành công"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
        500: {"description": "Internal server error"},
    },
)
async def upload_course_image(
    course_id: int,
    file: UploadFile = File(...),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Upload ảnh cho khóa học (chỉ admin)

    Args:
        course_id (int): ID của khóa học
        file (UploadFile): File ảnh cần upload
        storage_service (StorageService): Service xử lý lưu trữ
        admin_user (UserExcludeSecret): Thông tin admin đã xác thực
        db (Session): Session database

    Returns:
        FileUploadResponse: Thông tin file đã upload
    """
    # Kiểm tra xem khóa học có tồn tại không
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    try:
        # Upload file
        result = await storage_service.upload_course_image(file, course_id)

        # Cập nhật URL ảnh trong database
        course.thumbnailUrl = result["url"]
        db.commit()

        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi upload ảnh: {str(e)}",
        )


@router.post(
    "/course-image-temp",
    response_model=FileUploadResponse,
    summary="Upload ảnh khóa học tạm thời (Admin)",
    responses={
        200: {"description": "Upload thành công"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def upload_course_image_temp(
    file: UploadFile = File(...),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Upload ảnh khóa học tạm thời (không gắn với course cụ thể, dùng khi tạo course mới)
    """
    try:
        # Upload file với course_id = 0 (tạm thời)
        result = await storage_service.upload_course_image(file, 0)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi upload ảnh: {str(e)}",
        )
