from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    Schema cơ bản cho User

    Attributes:
        email (EmailStr): Email của user
        first_name (Optional[str]): Tên của người dùng
        last_name (Optional[str]): Họ của người dùng
    """
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserRegister(BaseModel):
    """
    Schema cho việc tạo User mới, kế thừa từ UserBase
    
    Attributes:
        password (str): Mật khẩu của user
    """
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    """
    Schema cho việc đăng nhập
    
    Attributes:
        username (str): Tên đăng nhập hoặc email
        password (str): Mật khẩu
    """
    username: str
    password: str
    remember_me: bool


class Token(BaseModel):
    """
    Schema cho token trả về khi đăng nhập thành công
    
    Attributes:
        access_token (str): JWT token
        token_type (str): Loại token (Bearer)
    """
    access_token: str
    token_type: str
