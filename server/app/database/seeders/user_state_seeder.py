"""
Module này chứa các hàm seeder cho model UserState.
"""
import logging
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.course import Course
from app.models.user_state import UserState

# Tạo logger
logger = logging.getLogger(__name__)

def seed_user_states(db: Session):
    """
    Tạo dữ liệu mẫu cho bảng user_states
    
    Args:
        db (Session): Database session
    """
    # Kiểm tra xem đã có user_states chưa
    existing_states = db.query(UserState).count()
    if existing_states > 0:
        logger.info(f"Đã có {existing_states} trạng thái người dùng trong database, bỏ qua seeding user_states.")
        return
    
    # Lấy tất cả users
    users = db.query(User).all()
    courses = db.query(Course).all()
    
    if not users or not courses:
        logger.warning("Không tìm thấy người dùng hoặc khóa học, không thể tạo user_states.")
        return
    
    for user in users:
        # Chọn ngẫu nhiên một khóa học làm current_course
        current_course = random.choice(courses) if courses else None
        
        # Tạo trạng thái người dùng
        state = UserState(
            user_id=user.id,
            last_active=datetime.utcnow(),
            current_course_id=current_course.id if current_course else None,
            streak_last_date=datetime.utcnow() - timedelta(days=random.randint(0, 3)),
            streak_count=random.randint(0, 30),
            total_points=random.randint(50, 500),
            level=random.randint(1, 10),
            xp_to_next_level=random.randint(10, 100),
            daily_goal=random.choice([15, 30, 45, 60]),
            daily_progress=random.randint(0, 60),
            completed_exercises=random.randint(0, 50),
            completed_courses=random.randint(0, 3),
            problems_solved=random.randint(0, 30),
            algorithms_progress=random.randint(0, 100),
            data_structures_progress=random.randint(0, 100),
            dynamic_programming_progress=random.randint(0, 100)
        )
        db.add(state)
    
    db.commit()
    logger.info(f"Đã tạo {len(users)} trạng thái người dùng mẫu.") 