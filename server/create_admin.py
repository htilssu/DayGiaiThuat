from app.database.database import SessionLocal
from sqlalchemy import text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin():
    db = SessionLocal()
    try:
        # Kiểm tra xem admin đã tồn tại chưa
        result = db.execute(
            text("SELECT id FROM users WHERE email = 'admin@example.com'")
        )
        existing_admin = result.fetchone()

        if existing_admin:
            # Cập nhật is_admin = true
            db.execute(
                text(
                    "UPDATE users SET is_admin = true WHERE email = 'admin@example.com'"
                )
            )
            print("Đã cập nhật quyền admin cho user hiện tại")
        else:
            # Tạo user admin mới
            hashed_password = pwd_context.hash("admin123")
            db.execute(
                text(
                    """
                INSERT INTO users (email, username, hashed_password, first_name, last_name, 
                                 bio, avatar, is_active, is_admin, created_at, updated_at)
                VALUES ('admin@example.com', 'admin', :hashed_password, 'Admin', 'User',
                       'Quản trị viên hệ thống', 'https://example.com/avatars/admin.jpg',
                       true, true, NOW(), NOW())
                """
                ),
                {"hashed_password": hashed_password},
            )
            print("Đã tạo user admin mới")

        db.commit()
        print("Hoàn thành!")

    except Exception as e:
        print(f"Lỗi: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
