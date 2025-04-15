from sqlalchemy import Boolean, Column, Integer, String
from app.database.database import Base

class User(Base):
    """
    Model đại diện cho bảng users trong database
    
    Attributes:
        id (int): ID của user, là primary key
        email (str): Email của user, phải là unique
        username (str): Tên đăng nhập của user
        hashed_password (str): Mật khẩu đã được mã hóa
        is_active (bool): Trạng thái hoạt động của tài khoản
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True) 