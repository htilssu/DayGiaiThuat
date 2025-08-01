from fastapi import APIRouter, Depends, HTTPException, status

from ..services.password_service import PasswordService, get_password_service
from ..schemas.password_schema import ChangePasswordSchema
from ..models.user_model import User
from ..schemas.user_profile_schema import UserUpdate, UserResponse, UserProfileResponse
from ..services.user_service import UserService, get_user_service
from ..services.profile_service import ProfileService, get_profile_service
from ..utils.utils import get_current_user, verify_password

router = APIRouter(prefix="/users", tags=["Người dùng"])


@router.get("", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Lấy thông tin người dùng hiện tại
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin của một người dùng cụ thể
    """
    # Kiểm tra người dùng tồn tại
    # TODO: Lấy thông tin người dùng từ cơ sở dữ liệu
    user = None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại"
        )

    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật thông tin profile người dùng hiện tại
    """
    # Cập nhật profile trong database
    updated_user = await user_service.update_user_profile(current_user.id, profile_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật thông tin người dùng",
        )

    return updated_user


@router.post("/me/change-password", response_model=dict)
async def change_user_password(
    data: ChangePasswordSchema,
    current_user: User = Depends(get_current_user),
    password_service: PasswordService = Depends(get_password_service),
):
    """
    Đổi mật khẩu người dùng
    """
    current_password = data.current_password
    new_password = data.new_password

    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng cung cấp mật khẩu hiện tại và mật khẩu mới",
        )

    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác",
        )

    # Cập nhật mật khẩu
    result = await password_service.update_password(current_user.id, new_password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật mật khẩu",
        )

    return {"message": "Đổi mật khẩu thành công"}


@router.post("/me/activities", response_model=UserResponse)
async def add_user_activity(
    activity_data: dict,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Thêm hoạt động mới cho người dùng hiện tại
    """
    updated_user = await user_service.add_activity(current_user.id, activity_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không thể thêm hoạt động"
        )

    # Cập nhật streak khi có hoạt động mới
    await user_service.update_streak(current_user.id)

    return updated_user


@router.post("/me/update-streak", response_model=UserResponse)
async def update_user_streak(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật streak cho người dùng hiện tại
    """
    updated_user = await user_service.update_streak(current_user.id)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không thể cập nhật streak"
        )

    return updated_user


@router.put("/me/learning-progress", response_model=UserResponse)
async def update_learning_progress(
    progress_data: dict,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật tiến độ học tập của người dùng hiện tại
    """
    updated_user = await user_service.update_learning_progress(
        current_user.id, progress_data
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật tiến độ học tập",
        )

    return updated_user


@router.put("/me/courses/{course_id}", response_model=UserResponse)
async def update_course_progress(
    course_id: str,
    progress_data: dict,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật tiến độ khóa học của người dùng hiện tại
    """
    progress = progress_data.get("progress", 0)

    updated_user = await user_service.update_course_progress(
        current_user.id, course_id, progress
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật tiến độ khóa học",
        )

    return updated_user


@router.post("/me/check-badges", response_model=UserResponse)
async def check_user_badges(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Kiểm tra và cập nhật huy hiệu cho người dùng hiện tại
    """
    updated_user = await user_service.update_badges(current_user.id)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không thể cập nhật huy hiệu"
        )

    return updated_user


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """
    Lấy thông tin profile đầy đủ của người dùng hiện tại
    bao gồm thống kê, tiến độ học tập, khóa học đã đăng ký, huy hiệu và lịch sử hoạt động
    """
    return await profile_service.get_user_profile(current_user.id)
