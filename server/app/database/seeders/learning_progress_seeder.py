"""
Module này chứa các hàm seeder cho model LearningProgress.
"""
import logging
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.learning_progress import LearningProgress
from app.models.user import User

# Tạo logger
logger = logging.getLogger(__name__)

def seed_learning_progress(db: Session):
    """
    Tạo dữ liệu mẫu cho bảng learning_progress
    
    Args:
        db (Session): Database session
    """
    # Kiểm tra xem đã có learning_progress chưa
    existing_progress = db.query(LearningProgress).count()
    if existing_progress > 0:
        logger.info(f"Đã có {existing_progress} tiến độ học tập trong database, bỏ qua seeding learning_progress.")
        return
    
    # Lấy tất cả users và courses
    users = db.query(User).all()
    courses = db.query(Course).all()
    
    if not users or not courses:
        logger.warning("Không tìm thấy người dùng hoặc khóa học, không thể tạo learning_progress.")
        return
    
    progress_records = []
    
    for user in users:
        # Mỗi người dùng đăng ký một vài khóa học ngẫu nhiên
        num_courses = random.randint(1, min(len(courses), 3))
        selected_courses = random.sample(courses, num_courses)
        
        for course in selected_courses:
            # Tạo tiến độ học tập
            progress_percent = random.uniform(0, 100)
            is_completed = progress_percent >= 100
            
            # Tạo danh sách bài học đã hoàn thành (mô phỏng)
            completed_lessons = [
                {"id": i, "title": f"Lesson {i}", "completed_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat()}
                for i in range(1, random.randint(1, 10)) if random.random() > 0.3
            ]
            
            # Tạo điểm các bài kiểm tra (mô phỏng)
            quiz_scores = {
                f"quiz_{i}": {
                    "score": random.randint(60, 100),
                    "max_score": 100,
                    "completed_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat()
                }
                for i in range(1, random.randint(1, 5)) if random.random() > 0.3
            }
            
            # Đảm bảo username không null khi tạo ghi chú
            username = user.username if user.username else f"user_{user.id}"
            
            progress = LearningProgress(
                user_id=user.id,
                course_id=course.id,
                progress_percent=progress_percent,
                last_accessed=datetime.utcnow() - timedelta(days=random.randint(0, 14)),
                is_completed=is_completed,
                completion_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if is_completed else None,
                notes=f"Ghi chú của {username} về khóa học {course.title}" if random.random() > 0.7 else None,
                favorite=random.random() > 0.7,
                completed_lessons=completed_lessons,
                quiz_scores=quiz_scores
            )
            progress_records.append(progress)
    
    # Thêm tất cả records cùng một lúc để tối ưu hiệu suất
    db.add_all(progress_records)
    db.commit()
    logger.info(f"Đã tạo {len(progress_records)} tiến độ học tập mẫu.") 