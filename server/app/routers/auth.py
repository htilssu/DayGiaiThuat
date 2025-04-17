from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Annotated

from app.schemas.user import UserCreate, UserLogin, Token, User
from app.models.user import User as UserModel
from app.utils.auth import (
    get_db,
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    oauth2_scheme
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Đăng ký tài khoản mới
    
    Args:
        user (UserCreate): Thông tin user cần đăng ký
        db (Session): Database session
        
    Returns:
        User: Thông tin user đã đăng ký
        
    Raises:
        HTTPException: 
            - 400: Email hoặc username đã tồn tại
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
    
    # Kiểm tra username đã tồn tại
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập đã được sử dụng"
        )
    
    try:
        # Tạo user mới
        hashed_password = get_password_hash(user.password)
        db_user = UserModel(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra khi tạo tài khoản"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 tiêu chuẩn token endpoint
    
    Args:
        response (Response): FastAPI response object để thiết lập cookie
        form_data (OAuth2PasswordRequestForm): Form data đăng nhập (username, password)
        db (Session): Database session
        
    Returns:
        Token: JWT token
        
    Raises:
        HTTPException: 
            - 401: Thông tin đăng nhập không chính xác
            - 400: Tài khoản bị vô hiệu hóa
    """
    # Tìm user theo username hoặc email
    user = db.query(UserModel).filter(
        (UserModel.username == form_data.username) |
        (UserModel.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    
    # Tạo access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Thiết lập cookie
    cookie_params = {
        "key": settings.COOKIE_NAME,
        "value": access_token,
        "max_age": settings.COOKIE_MAX_AGE,
        "httponly": settings.COOKIE_HTTPONLY,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE
    }
    
    # Chỉ thêm domain nếu được cấu hình
    if settings.COOKIE_DOMAIN:
        cookie_params["domain"] = settings.COOKIE_DOMAIN
    
    response.set_cookie(**cookie_params)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
) -> Any:
    """
    Đăng nhập và lấy token (giữ lại cho tương thích ngược)
    
    Args:
        response (Response): FastAPI response object để thiết lập cookie
        form_data (OAuth2PasswordRequestForm): Form data đăng nhập (username, password)
        db (Session): Database session
        
    Returns:
        Token: JWT token
        
    Raises:
        HTTPException: 
            - 401: Thông tin đăng nhập không chính xác
            - 400: Tài khoản bị vô hiệu hóa
    """
    # Gọi lại hàm login_for_access_token
    return await login_for_access_token(response, form_data, db)

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)) -> Any:
    """
    Lấy thông tin user hiện tại
    
    Args:
        current_user (UserModel): User hiện tại (từ token)
        
    Returns:
        User: Thông tin user
    """
    return current_user

@router.get("/test-token")
async def test_token(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Endpoint kiểm tra token có hợp lệ không
    
    Args:
        token (str): JWT token từ OAuth2PasswordBearer
        
    Returns:
        dict: Token được cung cấp
    """
    return {"token": token}

@router.post("/logout")
async def logout(response: Response):
    """
    Đăng xuất người dùng bằng cách xóa cookie
    
    Args:
        response (Response): FastAPI response object để xóa cookie
        
    Returns:
        dict: Thông báo đăng xuất thành công
    """
    # Xóa cookie
    cookie_params = {
        "key": settings.COOKIE_NAME,
        "httponly": settings.COOKIE_HTTPONLY,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE
    }
    
    # Chỉ thêm domain nếu được cấu hình
    if settings.COOKIE_DOMAIN:
        cookie_params["domain"] = settings.COOKIE_DOMAIN
    
    response.delete_cookie(**cookie_params)
    
    return {"message": "Đăng xuất thành công"} 