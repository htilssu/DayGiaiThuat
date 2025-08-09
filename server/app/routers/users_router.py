from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel

from ..schemas.password_schema import ChangePasswordSchema
from ..models.user_model import User
from ..schemas.user_profile_schema import UserUpdate, UserResponse, UserProfileResponse, UserExcludeSecret
from ..services.user_service import UserService, get_user_service
from ..services.profile_service import ProfileService, get_profile_service
from ..utils.utils import get_current_user, verify_password

router = APIRouter(prefix="/users", tags=["Người dùng"])


# Admin schemas
class AdminUserCreate(BaseModel):
    """Schema cho việc tạo người dùng mới (Admin)"""
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: bool = False
    is_active: bool = True
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class AdminUserUpdate(BaseModel):
    """Schema cho việc cập nhật thông tin người dùng (Admin)"""
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class AdminUserResponse(BaseModel):
    """Schema cho response thông tin người dùng (Admin)"""
    id: int
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: bool
    is_active: bool
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BulkDeleteUsersRequest(BaseModel):
    """Schema cho việc xóa nhiều người dùng cùng lúc"""
    user_ids: List[int]


class BulkDeleteUsersResponse(BaseModel):
    """Schema cho response xóa nhiều người dùng"""
    deleted_count: int
    failed_count: int
    failed_user_ids: List[int]
    message: str


def get_admin_user(current_user: UserExcludeSecret = Depends(get_current_user)):
    """Kiểm tra quyền admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này",
        )
    return current_user


# ===== ADMIN USER MANAGEMENT ROUTES (MUST BE BEFORE GENERIC ROUTES) =====

@router.post(
    "/admin",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo người dùng mới (Admin)",
    responses={
        201: {"description": "Tạo thành công"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        409: {"description": "Email hoặc username đã tồn tại"},
        500: {"description": "Internal server error"},
    },
)
async def create_user_admin(
    user_data: AdminUserCreate,
    user_service: UserService = Depends(get_user_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Tạo người dùng mới (chỉ admin)
    """
    # Kiểm tra email đã tồn tại
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email đã được sử dụng",
        )

    # Kiểm tra username đã tồn tại
    existing_username = await user_service.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username đã được sử dụng",
        )

    # Tạo user mới
    try:
        from ..schemas.auth_schema import UserRegister
        user_register = UserRegister(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name or "",
            last_name=user_data.last_name or "",
        )
        
        new_user = await user_service.create_user(user_register)
        
        # Cập nhật username và thông tin admin nếu cần
        if user_data.username or user_data.is_admin or not user_data.is_active:
            update_data = {}
            if user_data.username:
                update_data["username"] = user_data.username
            if user_data.is_admin is not None:
                update_data["is_admin"] = user_data.is_admin
            if user_data.is_active is not None:
                update_data["is_active"] = user_data.is_active
            
            await user_service.update_user_admin(new_user.id, update_data)
            # Refresh user data
            new_user = await user_service.get_user_by_id(new_user.id)
            if not new_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không thể cập nhật thông tin người dùng",
                )
        
        return AdminUserResponse(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            is_admin=new_user.is_admin,
            is_active=new_user.is_active,
            bio=new_user.bio,
            avatar_url=new_user.avatar,
            created_at=new_user.created_at.isoformat(),
            updated_at=new_user.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tạo người dùng: {str(e)}",
        )


@router.get(
    "/admin",
    response_model=List[AdminUserResponse],
    summary="Lấy danh sách tất cả người dùng (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
    },
)
async def get_all_users_admin(
    skip: int = Query(default=0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(default=100, ge=1, le=1000, description="Số bản ghi trả về"),
    user_service: UserService = Depends(get_user_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Lấy danh sách tất cả người dùng (chỉ admin)
    """
    users = await user_service.get_all_users(skip=skip, limit=limit)
    
    return [
        AdminUserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_admin=user.is_admin,
            is_active=user.is_active,
            bio=user.bio,
            avatar_url=user.avatar,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )
        for user in users
    ]


@router.get(
    "/admin/{user_id}",
    response_model=AdminUserResponse,
    summary="Lấy thông tin chi tiết người dùng (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy người dùng"},
    },
)
async def get_user_by_id_admin(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Lấy thông tin chi tiết người dùng theo ID (chỉ admin)
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_admin=user.is_admin,
        is_active=user.is_active,
        bio=user.bio,
        avatar_url=user.avatar,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )


@router.put(
    "/admin/{user_id}",
    response_model=AdminUserResponse,
    summary="Cập nhật thông tin người dùng (Admin)",
    responses={
        200: {"description": "Cập nhật thành công"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy người dùng"},
        409: {"description": "Email hoặc username đã tồn tại"},
        500: {"description": "Internal server error"},
    },
)
async def update_user_admin(
    user_id: int,
    user_data: AdminUserUpdate,
    user_service: UserService = Depends(get_user_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Cập nhật thông tin người dùng (chỉ admin)
    """
    # Kiểm tra người dùng tồn tại
    existing_user = await user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )

    # Kiểm tra email đã tồn tại (nếu có thay đổi email)
    if user_data.email and user_data.email != existing_user.email:
        email_exists = await user_service.get_user_by_email(user_data.email)
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email đã được sử dụng",
            )

    # Kiểm tra username đã tồn tại (nếu có thay đổi username)
    if user_data.username and user_data.username != existing_user.username:
        username_exists = await user_service.get_user_by_username(user_data.username)
        if username_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username đã được sử dụng",
            )

    # Cập nhật thông tin người dùng
    try:
        updated_user = await user_service.update_user_admin(
            user_id, user_data.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return AdminUserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            is_admin=updated_user.is_admin,
            is_active=updated_user.is_active,
            bio=updated_user.bio,
            avatar_url=updated_user.avatar,
            created_at=updated_user.created_at.isoformat(),
            updated_at=updated_user.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật người dùng: {str(e)}",
        )


@router.patch(
    "/admin/{user_id}/deactivate",
    response_model=AdminUserResponse,
    summary="Vô hiệu hóa người dùng (Admin)",
    responses={
        200: {"description": "Vô hiệu hóa thành công"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy người dùng"},
        500: {"description": "Internal server error"},
    },
)
async def deactivate_user_admin(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Vô hiệu hóa người dùng (chỉ admin)
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng đã bị vô hiệu hóa",
        )

    try:
        deactivated_user = await user_service.deactivate_user(user_id)
        if not deactivated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return AdminUserResponse(
            id=deactivated_user.id,
            email=deactivated_user.email,
            username=deactivated_user.username,
            first_name=deactivated_user.first_name,
            last_name=deactivated_user.last_name,
            is_admin=deactivated_user.is_admin,
            is_active=deactivated_user.is_active,
            bio=deactivated_user.bio,
            avatar_url=deactivated_user.avatar,
            created_at=deactivated_user.created_at.isoformat(),
            updated_at=deactivated_user.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể vô hiệu hóa người dùng: {str(e)}",
        )


@router.patch(
    "/admin/{user_id}/activate",
    response_model=AdminUserResponse,
    summary="Kích hoạt người dùng (Admin)",
    responses={
        200: {"description": "Kích hoạt thành công"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy người dùng"},
        500: {"description": "Internal server error"},
    },
)
async def activate_user_admin(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Kích hoạt người dùng (chỉ admin)
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng đã được kích hoạt",
        )

    try:
        activated_user = await user_service.activate_user(user_id)
        if not activated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return AdminUserResponse(
            id=activated_user.id,
            email=activated_user.email,
            username=activated_user.username,
            first_name=activated_user.first_name,
            last_name=activated_user.last_name,
            is_admin=activated_user.is_admin,
            is_active=activated_user.is_active,
            bio=activated_user.bio,
            avatar_url=activated_user.avatar,
            created_at=activated_user.created_at.isoformat(),
            updated_at=activated_user.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể kích hoạt người dùng: {str(e)}",
        )


@router.delete(
    "/admin/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa người dùng (Admin)",
    responses={
        200: {"description": "Xóa thành công"},
        400: {"description": "Không thể xóa người dùng"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy người dùng"},
        500: {"description": "Internal server error"},
    },
)
async def delete_user_admin(
    user_id: int,
    force: int = Query(
        default=0, ge=0, le=1, description="Force delete without checking dependencies"
    ),
    user_service: UserService = Depends(get_user_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Xóa người dùng (chỉ admin)
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )

    # Không cho phép xóa chính mình
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản của chính mình",
        )

    try:
        success = await user_service.delete_user(user_id, force=bool(force))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa người dùng. Có thể do người dùng đang có dữ liệu liên quan.",
            )
        
        return {"message": "Xóa người dùng thành công"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể xóa người dùng: {str(e)}",
        )


@router.delete(
    "/admin/bulk",
    response_model=BulkDeleteUsersResponse,
    summary="Xóa nhiều người dùng cùng lúc (Admin)",
    responses={
        200: {"description": "Xóa thành công"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def bulk_delete_users_admin(
    request: BulkDeleteUsersRequest,
    force: int = Query(
        default=0, ge=0, le=1, description="Force delete without checking dependencies"
    ),
    user_service: UserService = Depends(get_user_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Xóa nhiều người dùng cùng lúc (chỉ admin)
    """
    if not request.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Danh sách user_ids không được để trống",
        )

    # Loại bỏ ID của admin hiện tại khỏi danh sách xóa
    filtered_user_ids = [uid for uid in request.user_ids if uid != admin_user.id]
    
    if len(filtered_user_ids) != len(request.user_ids):
        # Có ít nhất một ID bị loại bỏ
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản của chính mình",
        )

    deleted_count = 0
    failed_count = 0
    failed_user_ids = []

    for user_id in filtered_user_ids:
        try:
            success = await user_service.delete_user(user_id, force=bool(force))
            if success:
                deleted_count += 1
            else:
                failed_count += 1
                failed_user_ids.append(user_id)
        except Exception:
            failed_count += 1
            failed_user_ids.append(user_id)

    message = f"Đã xóa thành công {deleted_count} người dùng"
    if failed_count > 0:
        message += f", {failed_count} người dùng không thể xóa"

    return BulkDeleteUsersResponse(
        deleted_count=deleted_count,
        failed_count=failed_count,
        failed_user_ids=failed_user_ids,
        message=message,
    )


# ===== REGULAR USER ROUTES =====

@router.get("", response_model=UserExcludeSecret)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Lấy thông tin người dùng hiện tại
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin người dùng theo ID
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chỉ có thể xem thông tin của chính mình",
        )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật thông tin hồ sơ người dùng hiện tại
    """
    try:
        updated_user = await user_service.update_user_profile(
            current_user.id, profile_data
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật hồ sơ: {str(e)}",
        )


@router.post("/me/change-password", response_model=dict)
async def change_user_password(
    data: ChangePasswordSchema,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Thay đổi mật khẩu người dùng hiện tại
    """
    # Kiểm tra mật khẩu hiện tại
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không đúng",
        )

    # Kiểm tra mật khẩu mới
    if data.new_password == data.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải khác mật khẩu hiện tại",
        )

    try:
        # Cập nhật mật khẩu
        await user_service.update_password(current_user.id, data.new_password)
        
        return {"message": "Thay đổi mật khẩu thành công"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể thay đổi mật khẩu: {str(e)}",
        )


@router.post("/me/activities", response_model=UserResponse)
async def add_user_activity(
    activity_data: dict,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Thêm hoạt động người dùng
    """
    try:
        updated_user = await user_service.add_activity(
            current_user.id, activity_data
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể thêm hoạt động: {str(e)}",
        )


@router.post("/me/update-streak", response_model=UserResponse)
async def update_user_streak(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật streak học tập của người dùng
    """
    try:
        updated_user = await user_service.update_streak(current_user.id)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật streak: {str(e)}",
        )


@router.put("/me/learning-progress", response_model=UserResponse)
async def update_learning_progress(
    progress_data: dict,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật tiến độ học tập của người dùng
    """
    try:
        updated_user = await user_service.update_learning_progress(
            current_user.id, progress_data
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật tiến độ học tập: {str(e)}",
        )


@router.put("/me/courses/{course_id}", response_model=UserResponse)
async def update_course_progress(
    course_id: str,
    progress_data: dict,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Cập nhật tiến độ khóa học của người dùng
    """
    try:
        progress = progress_data.get("progress", 0)
        updated_user = await user_service.update_course_progress(
            current_user.id, course_id, progress
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật tiến độ khóa học: {str(e)}",
        )


@router.post("/me/check-badges", response_model=UserResponse)
async def check_user_badges(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Kiểm tra và cập nhật badge của người dùng
    """
    try:
        updated_user = await user_service.update_badges(current_user.id)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể kiểm tra badge: {str(e)}",
        )


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """
    Lấy thông tin hồ sơ chi tiết của người dùng hiện tại
    """
    profile = await profile_service.get_user_profile(current_user.id)
    return profile
