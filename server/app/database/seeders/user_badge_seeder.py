"""
Module này chứa các hàm seeder cho việc gán huy hiệu cho người dùng.
"""
import logging
import random
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.badge import Badge

# Tạo logger
logger = logging.getLogger(__name__)

def seed_user_badges(db: Session):
    """
    Gán huy hiệu cho người dùng
    
    Args:
        db (Session): Database session
    """
    # Lấy tất cả users và badges
    users = db.query(User).all()
    badges = db.query(Badge).all()
    
    if not users or not badges:
        logger.warning("Không tìm thấy người dùng hoặc huy hiệu, không thể gán huy hiệu.")
        return
    
    # Gán huy hiệu "Người mới" cho tất cả người dùng
    newbie_badge = next((b for b in badges if b.name == "Người mới"), None)
    
    if newbie_badge:
        for user in users:
            # Kiểm tra xem người dùng đã có huy hiệu này chưa
            if newbie_badge not in user.badge_collection:
                user.badge_collection.append(newbie_badge)
    
    # Gán các huy hiệu khác ngẫu nhiên
    for user in users:
        # Chọn ngẫu nhiên 1-3 huy hiệu khác
        num_badges = random.randint(1, 3)
        selected_badges = random.sample(badges, min(num_badges, len(badges)))
        
        for badge in selected_badges:
            if badge not in user.badge_collection:
                user.badge_collection.append(badge)
    
    db.commit()
    logger.info("Đã gán huy hiệu cho người dùng.") 