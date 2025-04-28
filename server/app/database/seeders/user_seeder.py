"""
Module này chứa các hàm seeder cho model User.
"""
import logging
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.auth import get_password_hash

# Tạo logger
logger = logging.getLogger(__name__)

# Dữ liệu mẫu cho users
sample_users = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": True,
        "bio": "Quản trị viên hệ thống",
        "avatar_url": "https://ui-avatars.com/api/?name=Admin+User&background=random"
    },
    {
        "username": "user1",
        "email": "user1@example.com",
        "password": "user123",
        "first_name": "Nguyễn",
        "last_name": "Văn A",
        "is_active": True,
        "bio": "Học viên tích cực",
        "avatar_url": "https://ui-avatars.com/api/?name=Nguyen+Van+A&background=random"
    },
    {
        "username": "user2",
        "email": "user2@example.com",
        "password": "user123",
        "first_name": "Trần",
        "last_name": "Thị B",
        "is_active": True,
        "bio": "Đam mê học thuật toán",
        "avatar_url": "https://ui-avatars.com/api/?name=Tran+Thi+B&background=random"
    },
    {
        "username": "user3",
        "email": "user3@example.com",
        "password": "user123",
        "first_name": "Lê",
        "last_name": "Văn C",
        "is_active": True,
        "bio": "Đang tìm hiểu về cấu trúc dữ liệu",
        "avatar_url": "https://ui-avatars.com/api/?name=Le+Van+C&background=random"
    },
    {
        "username": "user4",
        "email": "user4@example.com",
        "password": "user123",
        "first_name": "Phạm",
        "last_name": "Thị D",
        "is_active": True,
        "bio": "Sinh viên năm cuối ngành Khoa học máy tính",
        "avatar_url": "https://ui-avatars.com/api/?name=Pham+Thi+D&background=random"
    }
]

def seed_users(db: Session):
    """
    Tạo dữ liệu mẫu cho bảng users
    
    Args:
        db (Session): Database session
    """
    # Kiểm tra xem có dữ liệu trong bảng user chưa
    existing_users = db.query(User).count()
    if existing_users > 0:
        logger.info(f"Đã có {existing_users} người dùng trong database, bỏ qua seeding users.")
        return
    
    for user_data in sample_users:
        # Hash mật khẩu
        hashed_password = get_password_hash(user_data["password"])
        
        # Tạo user mới
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            is_active=user_data["is_active"],
            bio=user_data["bio"],
            avatar_url=user_data["avatar_url"]
        )
        db.add(user)
    
    db.commit()
    logger.info(f"Đã tạo {len(sample_users)} người dùng mẫu.") 