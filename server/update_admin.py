from app.database.database import SessionLocal
from sqlalchemy import text


def update_admin():
    db = SessionLocal()
    try:
        # Cập nhật user admin bằng SQL trực tiếp
        result = db.execute(
            text("UPDATE users SET is_admin = true WHERE email = 'admin@example.com'")
        )
        db.commit()
        if result.rowcount > 0:
            print(f"Đã cập nhật {result.rowcount} user admin thành công")
        else:
            print("Không tìm thấy user admin với email admin@example.com")
    except Exception as e:
        print(f"Lỗi: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    update_admin()
