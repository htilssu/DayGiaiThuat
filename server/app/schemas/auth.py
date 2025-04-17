from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    """
    Schema cơ bản cho User
    
    Attributes:
        email (EmailStr): Email của user
        fullname (Optional[str]): Họ và tên đầy đủ của user
    """
    email: EmailStr
    fullname: Optional[str] = None

class UserCreate(UserBase):
    """
    Schema cho việc tạo User mới, kế thừa từ UserBase
    
    Attributes:
        password (str): Mật khẩu của user
    """
    password: str

class UserLogin(BaseModel):
    """
    Schema cho việc đăng nhập
    
    Attributes:
        username (str): Tên đăng nhập hoặc email
        password (str): Mật khẩu
    """
    username: str
    password: str

class Token(BaseModel):
    """
    Schema cho token trả về khi đăng nhập thành công
    
    Attributes:
        access_token (str): JWT token
        token_type (str): Loại token (Bearer)
    """
    access_token: str
    token_type: str 