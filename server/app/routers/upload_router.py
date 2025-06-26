from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.storage_service import StorageService, get_storage_service
from app.utils.utils import get_current_user
from app.schemas.user_profile_schema import UserExcludeSecret
from app.database.database import get_db

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    responses={404: {"description": "Not found"}},
)


class FileUploadResponse(BaseModel):
    key: str
    url: str
    content_type: str
    size: int


@router.post(
    "/user-avatar",
    response_model=FileUploadResponse,
    summary="Upload avatar người dùng",
    responses={
        200: {"description": "Upload thành công"},
        500: {"description": "Internal server error"},
    },
)
async def upload_user_avatar(
    file: UploadFile = File(...),
    storage_service: StorageService = Depends(get_storage_service),
    current_user: UserExcludeSecret = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload avatar cho người dùng hiện tại

    Args:
        file (UploadFile): File ảnh cần upload
        storage_service (StorageService): Service xử lý lưu trữ
        current_user (UserExcludeSecret): Thông tin người dùng hiện tại
        db (Session): Session database

    Returns:
        FileUploadResponse: Thông tin file đã upload
    """
    try:
        # Upload file
        result = await storage_service.upload_user_avatar(file, current_user.id)

        # Cập nhật URL avatar trong database
        from app.models.user_model import User

        user = db.query(User).filter(User.id == current_user.id).first()
        if user:
            user.avatarUrl = result["url"]
            db.commit()

        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi upload avatar: {str(e)}",
        )
