import json
import logging
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.course import Course
from app.models.badge import Badge
from app.models.user_state import UserState
from app.models.learning_progress import LearningProgress
from app.utils.auth import get_password_hash
from app.database.database import SessionLocal

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

# Dữ liệu mẫu cho courses
sample_courses = [
    {
        "title": "Nhập môn Thuật toán",
        "description": "Khóa học giới thiệu về cơ bản của thuật toán, độ phức tạp và các kỹ thuật phân tích thuật toán.",
        "thumbnail_url": "https://i.ibb.co/WnG0GQM/algo-intro.jpg",
        "level": "Beginner",
        "duration": 720,  # 12 giờ
        "price": 0.0,
        "is_published": True,
        "tags": "algorithm,introduction,beginner",
        "requirements": json.dumps(["Không yêu cầu kiến thức trước", "Máy tính cơ bản", "Kiến thức lập trình cơ bản"]),
        "what_you_will_learn": json.dumps([
            "Hiểu các khái niệm cơ bản về thuật toán",
            "Phân tích độ phức tạp thời gian và không gian",
            "Các thuật toán sắp xếp cơ bản",
            "Các thuật toán tìm kiếm cơ bản"
        ])
    },
    {
        "title": "Cấu trúc dữ liệu cơ bản",
        "description": "Tìm hiểu về các cấu trúc dữ liệu cơ bản như mảng, danh sách liên kết, ngăn xếp, hàng đợi và cây.",
        "thumbnail_url": "https://i.ibb.co/3dL7tK8/data-structure-basic.jpg",
        "level": "Beginner",
        "duration": 840,  # 14 giờ
        "price": 0.0,
        "is_published": True,
        "tags": "data-structures,arrays,linked-list,beginner",
        "requirements": json.dumps(["Kiến thức lập trình cơ bản", "Hiểu biết về biến và kiểu dữ liệu"]),
        "what_you_will_learn": json.dumps([
            "Hiểu và triển khai mảng và danh sách liên kết",
            "Hiểu và triển khai ngăn xếp và hàng đợi",
            "Hiểu và triển khai cây nhị phân cơ bản",
            "Ứng dụng của các cấu trúc dữ liệu trong các bài toán thực tế"
        ])
    },
    {
        "title": "Thuật toán nâng cao",
        "description": "Khóa học chuyên sâu về các thuật toán nâng cao như quy hoạch động, thuật toán tham lam, và chia để trị.",
        "thumbnail_url": "https://i.ibb.co/s5zW7ZQ/advanced-algo.jpg",
        "level": "Intermediate",
        "duration": 960,  # 16 giờ
        "price": 299000.0,
        "is_published": True,
        "tags": "algorithms,dynamic-programming,greedy,divide-and-conquer",
        "requirements": json.dumps(["Kiến thức về thuật toán cơ bản", "Hiểu biết về cấu trúc dữ liệu cơ bản"]),
        "what_you_will_learn": json.dumps([
            "Hiểu và áp dụng thuật toán quy hoạch động",
            "Hiểu và áp dụng thuật toán tham lam",
            "Hiểu và áp dụng kỹ thuật chia để trị",
            "Giải quyết các bài toán thuật toán phức tạp"
        ])
    },
    {
        "title": "Cấu trúc dữ liệu nâng cao",
        "description": "Tìm hiểu sâu về các cấu trúc dữ liệu phức tạp như cây AVL, B-tree, đồ thị và bảng băm.",
        "thumbnail_url": "https://i.ibb.co/wQZ1vhG/advanced-data-structure.jpg",
        "level": "Intermediate",
        "duration": 900,  # 15 giờ
        "price": 299000.0,
        "is_published": True,
        "tags": "data-structures,avl-tree,b-tree,graph,hash-table",
        "requirements": json.dumps(["Kiến thức về cấu trúc dữ liệu cơ bản", "Hiểu biết về thuật toán cơ bản"]),
        "what_you_will_learn": json.dumps([
            "Hiểu và triển khai cây AVL và B-tree",
            "Hiểu và triển khai đồ thị và các thuật toán trên đồ thị",
            "Hiểu và triển khai bảng băm",
            "Ứng dụng của các cấu trúc dữ liệu nâng cao trong các bài toán thực tế"
        ])
    },
    {
        "title": "Quy hoạch động cho người mới",
        "description": "Khóa học chuyên sâu về quy hoạch động, một kỹ thuật giải quyết bài toán bằng cách chia thành các bài toán con chồng chéo.",
        "thumbnail_url": "https://i.ibb.co/5xWHG9k/dynamic-programming.jpg",
        "level": "Intermediate",
        "duration": 780,  # 13 giờ
        "price": 199000.0,
        "is_published": True,
        "tags": "dynamic-programming,algorithms,optimization",
        "requirements": json.dumps(["Kiến thức về thuật toán cơ bản", "Hiểu biết về đệ quy"]),
        "what_you_will_learn": json.dumps([
            "Hiểu nguyên lý cơ bản của quy hoạch động",
            "Giải quyết các bài toán cơ bản bằng quy hoạch động",
            "Các kỹ thuật tối ưu hóa trong quy hoạch động",
            "Áp dụng quy hoạch động vào các bài toán thực tế"
        ])
    }
]

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

def seed_courses(db: Session):
    """
    Tạo dữ liệu mẫu cho bảng courses
    
    Args:
        db (Session): Database session
    """
    # Kiểm tra xem có dữ liệu trong bảng course chưa
    existing_courses = db.query(Course).count()
    if existing_courses > 0:
        logger.info(f"Đã có {existing_courses} khóa học trong database, bỏ qua seeding courses.")
        return
    
    for course_data in sample_courses:
        # Tạo course mới
        course = Course(
            title=course_data["title"],
            description=course_data["description"],
            thumbnail_url=course_data["thumbnail_url"],
            level=course_data["level"],
            duration=course_data["duration"],
            price=course_data["price"],
            is_published=course_data["is_published"],
            tags=course_data["tags"],
            requirements=course_data["requirements"],
            what_you_will_learn=course_data["what_you_will_learn"]
        )
        db.add(course)
    
    db.commit()
    logger.info(f"Đã tạo {len(sample_courses)} khóa học mẫu.")

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
            
            progress = LearningProgress(
                user_id=user.id,
                course_id=course.id,
                progress_percent=progress_percent,
                last_accessed=datetime.utcnow() - timedelta(days=random.randint(0, 14)),
                is_completed=is_completed,
                completion_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if is_completed else None,
                notes=f"Ghi chú của {user.username} về khóa học {course.title}" if random.random() > 0.7 else None,
                favorite=random.random() > 0.7,
                completed_lessons=completed_lessons,
                quiz_scores=quiz_scores
            )
            progress_records.append(progress)
    
    # Thêm tất cả records cùng một lúc để tối ưu hiệu suất
    db.add_all(progress_records)
    db.commit()
    logger.info(f"Đã tạo {len(progress_records)} tiến độ học tập mẫu.")

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