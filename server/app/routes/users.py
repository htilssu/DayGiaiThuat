from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta

from ..models.user import User
from ..schemas.user import (
    UserCreate, 
    User as UserResponse, 
    UserUpdate,
    Badge,
    Activity,
    UserStats,
    LearningProgress,
    CourseProgress
)
from ..dependencies.auth import get_current_user
from ..services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin người dùng hiện tại
    """
    # Lấy thông tin đầy đủ từ database
    user = await user_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin của một người dùng cụ thể
    """
    # Kiểm tra người dùng tồn tại
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    
    return user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật thông tin profile người dùng hiện tại
    """
    # Cập nhật profile trong database
    updated_user = await user_service.update_user_profile(
        current_user.id, 
        profile_data
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật thông tin người dùng"
        )
    
    return updated_user

@router.post("/me/change-password", response_model=dict)
async def change_user_password(
    password_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Đổi mật khẩu người dùng
    """
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng cung cấp mật khẩu hiện tại và mật khẩu mới"
        )
    
    # Kiểm tra mật khẩu hiện tại
    if not user_service.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác"
        )
    
    # Cập nhật mật khẩu
    result = await user_service.update_password(current_user.id, new_password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật mật khẩu"
        )
    
    return {"message": "Đổi mật khẩu thành công"}

@router.post("/me/activities", response_model=UserResponse)
async def add_user_activity(
    activity_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Thêm hoạt động mới cho người dùng hiện tại
    """
    updated_user = await user_service.add_activity(current_user.id, activity_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể thêm hoạt động"
        )
    
    # Cập nhật streak khi có hoạt động mới
    await user_service.update_streak(current_user.id)
    
    return updated_user

@router.post("/me/update-streak", response_model=UserResponse)
async def update_user_streak(
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật streak cho người dùng hiện tại
    """
    updated_user = await user_service.update_streak(current_user.id)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật streak"
        )
    
    return updated_user

@router.put("/me/learning-progress", response_model=UserResponse)
async def update_learning_progress(
    progress_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật tiến độ học tập của người dùng hiện tại
    """
    updated_user = await user_service.update_learning_progress(current_user.id, progress_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật tiến độ học tập"
        )
    
    return updated_user

@router.put("/me/courses/{course_id}", response_model=UserResponse)
async def update_course_progress(
    course_id: str,
    progress_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật tiến độ khóa học của người dùng hiện tại
    """
    progress = progress_data.get("progress", 0)
    
    updated_user = await user_service.update_course_progress(
        current_user.id, 
        course_id,
        progress
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật tiến độ khóa học"
        )
    
    return updated_user

@router.post("/me/check-badges", response_model=UserResponse)
async def check_user_badges(
    current_user: User = Depends(get_current_user)
):
    """
    Kiểm tra và cập nhật huy hiệu cho người dùng hiện tại
    """
    updated_user = await user_service.update_badges(current_user.id)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật huy hiệu"
        )
    
    return updated_user 