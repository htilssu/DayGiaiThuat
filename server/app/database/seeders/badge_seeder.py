"""
Module này chứa các hàm seeder cho model Badge.
"""
import logging
from sqlalchemy.orm import Session

from app.models.badge import Badge

# Tạo logger
logger = logging.getLogger(__name__)

# Dữ liệu mẫu cho badges
sample_badges = [
    {
        "name": "Người mới",
        "icon": "🌱",
        "image_url": "https://i.ibb.co/kJtGh7n/newbie-badge.png",
        "description": "Huy hiệu dành cho người mới tham gia hệ thống",
        "category": "Tiến độ",
        "criteria": "Đăng ký tài khoản thành công",
        "points": 10,
        "rarity": "Common",
        "is_hidden": False,
        "is_active": True
    },
    {
        "name": "Hoàn thành khóa học đầu tiên",
        "icon": "🎓",
        "image_url": "https://i.ibb.co/7vFq2PF/first-course-badge.png",
        "description": "Hoàn thành 100% một khóa học bất kỳ",
        "category": "Thành tựu",
        "criteria": "Hoàn thành một khóa học bất kỳ",
        "points": 50,
        "rarity": "Uncommon",
        "is_hidden": False,
        "is_active": True
    },
    {
        "name": "Chuyên gia thuật toán",
        "icon": "🧠",
        "image_url": "https://i.ibb.co/DWVxkrx/algo-expert.png",
        "description": "Hoàn thành tất cả các khóa học về thuật toán",
        "category": "Thành tựu",
        "criteria": "Hoàn thành các khóa học thuật toán",
        "points": 200,
        "rarity": "Rare",
        "is_hidden": False,
        "is_active": True
    },
    {
        "name": "Streak 7 ngày",
        "icon": "🔥",
        "image_url": "https://i.ibb.co/JHcvYCW/streak-7-badge.png",
        "description": "Duy trì streak học tập 7 ngày liên tục",
        "category": "Tiến độ",
        "criteria": "Học tập 7 ngày liên tục",
        "points": 70,
        "rarity": "Uncommon",
        "is_hidden": False,
        "is_active": True
    },
    {
        "name": "Người khám phá",
        "icon": "🔍",
        "image_url": "https://i.ibb.co/HxPT8F5/explorer-badge.png",
        "description": "Truy cập vào tất cả các phần của hệ thống",
        "category": "Khám phá",
        "criteria": "Truy cập vào tất cả các tính năng chính",
        "points": 30,
        "rarity": "Common",
        "is_hidden": False,
        "is_active": True
    }
]

def seed_badges(db: Session):
    """
    Tạo dữ liệu mẫu cho bảng badges
    
    Args:
        db (Session): Database session
    """
    # Kiểm tra xem có dữ liệu trong bảng badge chưa
    existing_badges = db.query(Badge).count()
    if existing_badges > 0:
        logger.info(f"Đã có {existing_badges} huy hiệu trong database, bỏ qua seeding badges.")
        return
    
    for badge_data in sample_badges:
        # Tạo badge mới
        badge = Badge(
            name=badge_data["name"],
            icon=badge_data["icon"],
            image_url=badge_data["image_url"],
            description=badge_data["description"],
            category=badge_data["category"],
            criteria=badge_data["criteria"],
            points=badge_data["points"],
            rarity=badge_data["rarity"],
            is_hidden=badge_data["is_hidden"],
            is_active=badge_data["is_active"]
        )
        db.add(badge)
    
    db.commit()
    logger.info(f"Đã tạo {len(sample_badges)} huy hiệu mẫu.") 