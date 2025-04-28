"""
Module chịu trách nhiệm khởi tạo dữ liệu mẫu cho ứng dụng.
"""
import logging
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.seeders.user_seeder import seed_users
from app.database.seeders.course_seeder import seed_courses
from app.database.seeders.badge_seeder import seed_badges
from app.database.seeders.user_state_seeder import seed_user_states
from app.database.seeders.learning_progress_seeder import seed_learning_progress
from app.database.seeders.user_badge_seeder import seed_user_badges

# Tạo logger
logger = logging.getLogger(__name__)

def run_seeder():
    """
    Chạy tất cả các hàm seed để tạo dữ liệu mẫu
    """
    db = SessionLocal()
    try:
        logger.info("Bắt đầu seeding database...")
        
        # Thực hiện seed theo thứ tự phù hợp với các ràng buộc khóa ngoại
        seed_users(db)
        seed_courses(db)
        seed_badges(db)
        seed_user_states(db)
        seed_learning_progress(db)
        seed_user_badges(db)
        
        logger.info("Seeding database hoàn tất!")
    except Exception as e:
        logger.error(f"Lỗi khi seeding database: {str(e)}")
    finally:
        db.close() 