from datetime import timedelta
from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User as UserModel
from app.schemas.auth import UserCreate, UserLogin, Token
from app.schemas.user_profile import User
from app.utils.auth import (
    get_db,
    verify_password,
    get_password_hash,
    create_access_token,
    set_auth_cookie,
    clear_auth_cookie,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        response: Response,
        user: UserCreate,
        db: Session = Depends(get_db)
) -> Any:
    """
    Đăng ký tài khoản mới và trả về token đăng nhập
    
    Args:
        response (Response): FastAPI response object để thiết lập cookie
        user (UserCreate): Thông tin user cần đăng ký (email, password, fullname)
        db (Session): Database session
        
    Returns:
        Token: JWT token
        
    Raises:
        HTTPException: 
            - 400: Email đã tồn tại
            - 422: Dữ liệu không hợp lệ
    """
    # Validate dữ liệu
    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Mật khẩu phải có ít nhất 6 ký tự"
        )

    # Kiểm tra email đã tồn tại
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký"
        )

    try:
        # Tạo user mới với username là None
        hashed_password = get_password_hash(user.password)
        db_user = UserModel(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Tạo access token - Luôn sử dụng email vì username là None
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=timedelta(minutes=60 * 24 * 30)
        )

        # Thiết lập cookie sử dụng hàm tiện ích
        set_auth_cookie(response, access_token)

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra khi tạo tài khoản"
        )


@router.post("/login", response_model=Token)
async def login(
        response: Response,
        data: UserLogin,
        db: Session = Depends(get_db)
) -> Any:
    """
    Đăng nhập và lấy token

    :param db: Database session
    :param response: FastAPI response object để thiết lập cookie
    :param data: Thông tin đăng nhập (username/email, password)
        
    :returns: Token
        
    :raises HTTPException: - 401: Thông tin đăng nhập không chính xác
                           - 400: Tài khoản đã bị vô hiệu hóa
    """
    # Tìm user theo username hoặc email
    user = db.query(UserModel).filter(
        or_(UserModel.username == data.username, UserModel.email == data.username)).first()

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị vô hiệu hóa"
        )

    # Tạo access token - Sử dụng email nếu username là null
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(
        data=token_data, expires_delta=timedelta(minutes=60 * 24 * 30) if data.remember_me else None
    )

    # Thiết lập cookie sử dụng hàm tiện ích
    set_auth_cookie(response, access_token)

    return {"access_token": access_token, "token_type": "bearer"}

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
