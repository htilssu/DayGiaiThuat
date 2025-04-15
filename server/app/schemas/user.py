from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """
    Schema cơ bản cho User
    
    Attributes:
        email (EmailStr): Email của user
        username (str): Tên đăng nhập của user
    """
    email: EmailStr
    username: str

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

class User(UserBase):
    """
    Schema cho thông tin User trả về, kế thừa từ UserBase
    
    Attributes:
        id (int): ID của user
        is_active (bool): Trạng thái hoạt động của tài khoản
    """
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    """
    Schema cho token trả về khi đăng nhập thành công
    
    Attributes:
        access_token (str): JWT token
        token_type (str): Loại token (Bearer)
    """
    access_token: str
    token_type: str 