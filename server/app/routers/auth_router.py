from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.models.user_model import User as UserModel
from app.schemas.auth_schema import UserRegister, UserLogin, LoginResponse
from app.utils.utils import (
    get_db,
    verify_password,
    create_access_token,
    set_auth_cookie,
    clear_auth_cookie,
)
from app.services.user_service import UserService, get_user_service

router = APIRouter(
    prefix="/auth",
    tags=["Xác thực"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
        400: {"description": "Bad request"},
    },
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Created"},
        400: {"description": "Dữ liệu không hợp lệ"},
    },
)
async def register(
    response: Response,
    user: UserRegister,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Đăng ký tài khoản mới và trả về token đăng nhập
    """

    new_user = await user_service.create_user(user)
    # Tạo access token - Sử dụng email nếu username là null
    token_data = {"sub": str(new_user.id)}
    access_token = create_access_token(
        data=token_data,
    )

    set_auth_cookie(response, access_token)

    return {"message": "Đăng ký thành công", "access_token": access_token}


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        200: {"description": "OK"},
        400: {
            "description": "Mật khẩu không chính xác hoặc tài khoản đã bị vô hiệu hóa"
        },
        401: {"description": "Thông tin đăng nhập không chính xác"},
        404: {"description": "Tài khoản không tồn tại"},
        500: {"description": "Internal server error"},
    },
)
async def login(
    response: Response, data: UserLogin, db: Session = Depends(get_db)
) -> Any:
    """
    Đăng nhập và lấy token

    :param db: Database session
    :param response: FastAPI response object để thiết lập cookie
    :param data: Thông tin đăng nhập (username/email, password)

    :returns: Token
    """
    # Tìm user theo username hoặc email
    is_email = "@" in data.username
    if is_email:
        user = db.query(UserModel).filter(UserModel.email == data.username).first()
    else:
        user = db.query(UserModel).filter(UserModel.username == data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài khoản không tồn tại",
        )

    if not verify_password(data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản đã bị vô hiệu hóa",
        )

    # Tạo access token - Sử dụng email nếu username là null
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(
        data=token_data,
    )

    # Thiết lập cookie sử dụng hàm tiện ích
    set_auth_cookie(response, access_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        },
    }


@router.post("/logout")
async def logout(response: Response):
    """
    Đăng xuất người dùng bằng cách xóa cookie

    Args:
        response (Response): FastAPI response object để xóa cookie

    Returns:
        dict: Thông báo đăng xuất thành công
    """
    # Xóa cookie sử dụng hàm tiện ích
    clear_auth_cookie(response)

    return {"message": "Đăng xuất thành công"}
