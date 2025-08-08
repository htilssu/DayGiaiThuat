#!/usr/bin/env python3
"""
Script để tạo admin user hoặc cập nhật user hiện tại thành admin
"""

import asyncio
import sys
import os

# Add the server directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db
from app.models.user_model import User
from app.services.user_service import UserService
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def create_admin_user():
    """Tạo admin user mới"""
    db = await anext(get_db())
    user_service = UserService(db)
    
    # Thông tin admin user
    admin_data = {
        "email": "admin@example.com",
        "username": "admin",
        "hashed_password": get_password_hash("admin123"),
        "first_name": "Admin",
        "last_name": "User",
        "is_admin": True,
        "is_active": True,
        "bio": "Administrator account"
    }
    
    # Kiểm tra xem admin user đã tồn tại chưa
    existing_admin = await user_service.get_user_by_email(admin_data["email"])
    if existing_admin:
        print("Admin user với email admin@example.com đã tồn tại!")
        return existing_admin
    
    # Tạo admin user mới
    try:
        # Tạo user object
        admin_user = User(**admin_data)
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print("✅ Đã tạo admin user thành công!")
        print(f"Email: {admin_user.email}")
        print(f"Username: {admin_user.username}")
        print("Password: admin123")
        print(f"Admin: {admin_user.is_admin}")
        
        return admin_user
    except Exception as e:
        print(f"❌ Lỗi khi tạo admin user: {e}")
        await db.rollback()
        return None


async def update_user_to_admin(email: str):
    """Cập nhật user hiện tại thành admin"""
    db = await anext(get_db())
    user_service = UserService(db)
    
    # Tìm user theo email
    user = await user_service.get_user_by_email(email)
    if not user:
        print(f"❌ Không tìm thấy user với email: {email}")
        return None
    
    # Cập nhật thành admin
    try:
        user.is_admin = True
        user.is_active = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        print("✅ Đã cập nhật user thành admin!")
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        print(f"Admin: {user.is_admin}")
        
        return user
    except Exception as e:
        print(f"❌ Lỗi khi cập nhật user: {e}")
        await db.rollback()
        return None


async def list_users():
    """Liệt kê tất cả users"""
    db = await anext(get_db())
    user_service = UserService(db)
    users = await user_service.get_all_users()
    
    print("\n📋 Danh sách users:")
    print("-" * 80)
    print(f"{'ID':<5} {'Email':<25} {'Username':<15} {'Admin':<8} {'Active':<8}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.id:<5} {user.email:<25} {user.username:<15} {str(user.is_admin):<8} {str(user.is_active):<8}")


async def main():
    print("🔧 Admin User Management Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Cách sử dụng:")
        print("  python create_admin_user.py create    # Tạo admin user mới")
        print("  python create_admin_user.py update <email>  # Cập nhật user thành admin")
        print("  python create_admin_user.py list      # Liệt kê tất cả users")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        print("🆕 Tạo admin user mới...")
        await create_admin_user()
    
    elif command == "update":
        if len(sys.argv) < 3:
            print("❌ Vui lòng cung cấp email: python create_admin_user.py update <email>")
            return
        
        email = sys.argv[2]
        print(f"🔄 Cập nhật user {email} thành admin...")
        await update_user_to_admin(email)
    
    elif command == "list":
        print("📋 Liệt kê users...")
        await list_users()
    
    else:
        print(f"❌ Lệnh không hợp lệ: {command}")


if __name__ == "__main__":
    asyncio.run(main())
