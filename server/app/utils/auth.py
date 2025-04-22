from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import SessionLocal
from app.models.user import User
from app.utils.oauth2 import OAuth2PasswordCookie

# Cấu hình bảo mật
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Cấu hình mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Sử dụng đường dẫn tương đối để đảm bảo hoạt động đúng với các prefix
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")
# Tạo instance mới sử dụng cookie
oauth2_cookie_scheme = OAuth2PasswordCookie(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def get_db():
    """
    Dependency để lấy database session
    
    Returns:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Xác thực mật khẩu
    
    Args:
        plain_password (str): Mật khẩu gốc
        hashed_password (str): Mật khẩu đã được hash
        
    Returns:
        bool: True nếu mật khẩu đúng, False nếu sai
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash mật khẩu
    
    Args:
        password (str): Mật khẩu cần hash
        
    Returns:
        str: Mật khẩu đã được hash
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT token
    
    Args:
        data (dict): Dữ liệu cần mã hóa trong token
        expires_delta (Optional[timedelta]): Thời gian hết hạn của token
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    time_now = datetime.now()
    if expires_delta:
        expire = time_now + expires_delta
    else:
        expire = time_now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode.update({"iat": time_now})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Lấy thông tin user hiện tại từ token
    
    Args:
        token (str): JWT token
        db (Session): Database session
        
    Returns:
        User: Thông tin user
        
    Raises:
        HTTPException: 
            - 401: Token không hợp lệ hoặc hết hạn
            - 404: Không tìm thấy user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user 

async def get_current_user_from_cookie(token: str = Depends(oauth2_cookie_scheme), db: Session = Depends(get_db)) -> User:
    """
    Lấy thông tin user hiện tại từ token trong cookie
    
    Args:
        token (str): JWT token từ cookie
        db (Session): Database session
        
    Returns:
        User: Thông tin user
        
    Raises:
        HTTPException: 
            - 401: Token không hợp lệ hoặc hết hạn
            - 404: Không tìm thấy user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user 

def set_auth_cookie(response: Response, token: str) -> None:
    """
    Thiết lập cookie chứa JWT token
    
    Args:
        response (Response): Đối tượng Response của FastAPI
        token (str): JWT token cần lưu vào cookie
    """
    cookie_params = {
        "key": settings.COOKIE_NAME,
        "value": token,
        "httponly": settings.COOKIE_HTTPONLY,
        "max_age": settings.COOKIE_MAX_AGE,
        "samesite": settings.COOKIE_SAMESITE,
        "secure": settings.COOKIE_SECURE
    }
    
    # Chỉ thêm domain nếu có cấu hình
    if settings.COOKIE_DOMAIN:
        cookie_params["domain"] = settings.COOKIE_DOMAIN
        
    response.set_cookie(**cookie_params)
    
def clear_auth_cookie(response: Response) -> None:
    """
    Xóa cookie xác thực khi đăng xuất
    
    Args:
        response (Response): Đối tượng Response của FastAPI
    """
    cookie_params = {
        "key": settings.COOKIE_NAME,
        "value": "",
        "expires": 0,
        "max_age": 0,
        "httponly": settings.COOKIE_HTTPONLY,
        "samesite": settings.COOKIE_SAMESITE,
        "secure": settings.COOKIE_SECURE
    }
    
    # Chỉ thêm domain nếu có cấu hình
    if settings.COOKIE_DOMAIN:
        cookie_params["domain"] = settings.COOKIE_DOMAIN
        
    response.delete_cookie(**cookie_params) 