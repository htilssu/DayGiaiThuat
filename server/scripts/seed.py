"""
Script để tạo dữ liệu mẫu cho ứng dụng.

Cách sử dụng:
    python -m scripts.seed
"""

import json
import logging
import random
from datetime import datetime
from typing import List
from app.database.database import SessionLocal

from passlib.context import CryptContext
from app.models.badge_model import Badge
from app.models.course_model import Course
from app.models.exercise_model import Exercise
from app.models.topic_model import Topic
from app.models.test_model import Test
from app.models.user_model import User
from app.models.user_state_model import UserState

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password context để hash mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_topics() -> List[Topic]:
    """
    Tạo dữ liệu mẫu cho bảng topics

    Returns:
        List[Topic]: Danh sách các topic đã tạo
    """
    logger.info("Tạo dữ liệu mẫu cho Topics...")

    topics_data = [
        {
            "name": "Cấu trúc dữ liệu",
            "description": "Các cấu trúc dữ liệu cơ bản và nâng cao",
        },
        {
            "name": "Thuật toán sắp xếp",
            "description": "Các thuật toán sắp xếp và phân tích độ phức tạp",
        },
        {
            "name": "Thuật toán tìm kiếm",
            "description": "Các thuật toán tìm kiếm và ứng dụng",
        },
        {
            "name": "Quy hoạch động",
            "description": "Phương pháp quy hoạch động và các bài toán kinh điển",
        },
        {"name": "Đồ thị", "description": "Thuật toán trên đồ thị và ứng dụng"},
    ]

    db = SessionLocal()
    topics = []

    try:
        for topic_data in topics_data:
            topic = Topic(**topic_data)
            db.add(topic)
            topics.append(topic)

        db.commit()
        for topic in topics:
            db.refresh(topic)

        logger.info(f"Đã tạo {len(topics)} topics")
        return topics
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi tạo topics: {str(e)}")
        return []
    finally:
        db.close()


def create_exercises(topics: List[Topic]) -> List[Exercise]:
    """
    Tạo dữ liệu mẫu cho bảng exercises

    Args:
        topics (List[Topic]): Danh sách các topic để liên kết

    Returns:
        List[Exercise]: Danh sách các exercise đã tạo
    """
    logger.info("Tạo dữ liệu mẫu cho Exercises...")

    exercises_data = [
        {
            "name": "Cài đặt Stack và Queue",
            "description": "Cài đặt cấu trúc dữ liệu Stack và Queue sử dụng mảng và danh sách liên kết",
            "category": "Implementation",
            "difficulty": "Easy",
            "constraint": "Thời gian thực thi O(1) cho các thao tác cơ bản",
            "topic_id": 1,
        },
        {
            "name": "Cài đặt Heap",
            "description": "Cài đặt cấu trúc dữ liệu Heap và các thao tác cơ bản",
            "category": "Implementation",
            "difficulty": "Medium",
            "constraint": "Thời gian thực thi O(log n) cho các thao tác cơ bản",
            "topic_id": 1,
        },
        {
            "name": "Quicksort",
            "description": "Cài đặt thuật toán Quicksort và phân tích độ phức tạp",
            "category": "Algorithm",
            "difficulty": "Medium",
            "constraint": "Thời gian thực thi trung bình O(n log n)",
            "topic_id": 2,
        },
        {
            "name": "Binary Search",
            "description": "Cài đặt thuật toán Binary Search và các biến thể",
            "category": "Algorithm",
            "difficulty": "Easy",
            "constraint": "Thời gian thực thi O(log n)",
            "topic_id": 3,
        },
        {
            "name": "Bài toán Knapsack",
            "description": "Giải quyết bài toán Knapsack bằng phương pháp quy hoạch động",
            "category": "Dynamic Programming",
            "difficulty": "Hard",
            "constraint": "Giới hạn bộ nhớ và tối ưu hóa không gian",
            "topic_id": 4,
        },
        {
            "name": "Thuật toán Dijkstra",
            "description": "Cài đặt thuật toán Dijkstra tìm đường đi ngắn nhất trên đồ thị",
            "category": "Graph",
            "difficulty": "Medium",
            "constraint": "Thời gian thực thi O((V+E)logV)",
            "topic_id": 5,
        },
    ]

    db = SessionLocal()
    exercises = []

    try:
        for exercise_data in exercises_data:
            exercise = Exercise(**exercise_data)
            db.add(exercise)
            exercises.append(exercise)

        db.commit()
        for exercise in exercises:
            db.refresh(exercise)

        logger.info(f"Đã tạo {len(exercises)} exercises")
        return exercises
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi tạo exercises: {str(e)}")
        return []
    finally:
        db.close()


def create_tests(topics: List[Topic]) -> List[Test]:
    """
    Tạo dữ liệu mẫu cho bảng tests

    Args:
        topics (List[Topic]): Danh sách các topic để liên kết

    Returns:
        List[Test]: Danh sách các test đã tạo
    """
    logger.info("Tạo dữ liệu mẫu cho Tests...")

    tests_data = [
        {"name": "Kiểm tra kiến thức cấu trúc dữ liệu", "topic_id": 1},
        {"name": "Kiểm tra thuật toán sắp xếp", "topic_id": 2},
        {"name": "Kiểm tra thuật toán tìm kiếm", "topic_id": 3},
        {"name": "Kiểm tra quy hoạch động", "topic_id": 4},
        {"name": "Kiểm tra thuật toán đồ thị", "topic_id": 5},
    ]

    db = SessionLocal()
    tests = []

    try:
        for test_data in tests_data:
            test = Test(**test_data)
            db.add(test)
            tests.append(test)

        db.commit()
        for test in tests:
            db.refresh(test)

        logger.info(f"Đã tạo {len(tests)} tests")
        return tests
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi tạo tests: {str(e)}")
        return []
    finally:
        db.close()


def create_badges() -> List[Badge]:
    """
    Tạo dữ liệu mẫu cho bảng badges

    Returns:
        List[Badge]: Danh sách các badge đã tạo
    """
    logger.info("Tạo dữ liệu mẫu cho Badges...")

    badges_data = [
        {
            "name": "Người mới bắt đầu",
            "icon": "🔰",
            "description": "Hoàn thành đăng ký và thiết lập hồ sơ",
            "category": "Thành tựu",
            "criteria": "Đăng ký tài khoản và hoàn thiện hồ sơ",
            "points": 10,
            "rarity": "Phổ biến",
            "is_hidden": False,
        },
        {
            "name": "Học viên chăm chỉ",
            "icon": "📚",
            "description": "Hoàn thành 5 bài học liên tiếp",
            "category": "Tiến độ",
            "criteria": "Hoàn thành 5 bài học liên tiếp không bỏ ngày nào",
            "points": 20,
            "rarity": "Phổ biến",
            "is_hidden": False,
        },
        {
            "name": "Cây bút vàng",
            "icon": "✍️",
            "description": "Viết 10 bài thảo luận có ích",
            "category": "Cộng đồng",
            "criteria": "Viết 10 bài thảo luận được đánh giá cao",
            "points": 30,
            "rarity": "Hiếm",
            "is_hidden": False,
        },
        {
            "name": "Nhà giải thuật toán",
            "icon": "🧠",
            "description": "Giải quyết 20 bài tập thuật toán",
            "category": "Kỹ năng",
            "criteria": "Hoàn thành 20 bài tập thuật toán với điểm số tối thiểu 80%",
            "points": 50,
            "rarity": "Hiếm",
            "is_hidden": False,
        },
        {
            "name": "Bậc thầy quy hoạch động",
            "icon": "🏆",
            "description": "Giải quyết tất cả các bài tập quy hoạch động",
            "category": "Kỹ năng",
            "criteria": "Hoàn thành tất cả bài tập quy hoạch động với điểm số tối thiểu 90%",
            "points": 100,
            "rarity": "Cực hiếm",
            "is_hidden": False,
        },
    ]

    db = SessionLocal()
    badges = []

    try:
        for badge_data in badges_data:
            badge = Badge(**badge_data)
            db.add(badge)
            badges.append(badge)

        db.commit()
        for badge in badges:
            db.refresh(badge)

        logger.info(f"Đã tạo {len(badges)} badges")
        return badges
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi tạo badges: {str(e)}")
        return []
    finally:
        db.close()


def create_courses() -> List[Course]:
    """
    Tạo dữ liệu mẫu cho bảng courses

    Returns:
        List[Course]: Danh sách các course đã tạo
    """
    logger.info("Tạo dữ liệu mẫu cho Courses...")

    courses_data = [
        {
            "title": "Nhập môn Cấu trúc dữ liệu và Giải thuật",
            "description": "Khóa học giới thiệu về các cấu trúc dữ liệu và thuật toán cơ bản",
            "thumbnail_url": "https://example.com/thumbnails/dsa-intro.jpg",
            "level": "Beginner",
            "duration": 600,  # 10 giờ
            "price": 0.0,  # Miễn phí
            "is_published": True,
            "tags": "algorithm,data structure,beginner",
            "requirements": json.dumps(
                [
                    "Kiến thức lập trình cơ bản",
                    "Hiểu biết về một ngôn ngữ lập trình (Python, Java, C++)",
                ]
            ),
            "what_you_will_learn": json.dumps(
                [
                    "Hiểu về các cấu trúc dữ liệu cơ bản",
                    "Phân tích độ phức tạp thuật toán",
                    "Cài đặt các thuật toán sắp xếp và tìm kiếm",
                    "Giải quyết các bài toán cơ bản",
                ]
            ),
            "learning_path": json.dumps(
                {
                    "units": [
                        {
                            "id": 1,
                            "title": "Giới thiệu",
                            "lessons": [
                                {"id": 1, "title": "Tổng quan về DSA", "duration": 15},
                                {
                                    "id": 2,
                                    "title": "Phân tích độ phức tạp",
                                    "duration": 20,
                                },
                            ],
                        },
                        {
                            "id": 2,
                            "title": "Cấu trúc dữ liệu cơ bản",
                            "lessons": [
                                {
                                    "id": 3,
                                    "title": "Array và Linked List",
                                    "duration": 30,
                                },
                                {"id": 4, "title": "Stack và Queue", "duration": 25},
                            ],
                        },
                    ]
                }
            ),
        },
        {
            "title": "Thuật toán nâng cao",
            "description": "Khóa học đi sâu vào các thuật toán nâng cao và kỹ thuật giải quyết vấn đề",
            "thumbnail_url": "https://example.com/thumbnails/advanced-algo.jpg",
            "level": "Advanced",
            "duration": 900,  # 15 giờ
            "price": 49.99,
            "is_published": True,
            "tags": "algorithm,advanced,optimization",
            "requirements": json.dumps(
                [
                    "Kiến thức vững về cấu trúc dữ liệu cơ bản",
                    "Hiểu biết về độ phức tạp thuật toán",
                    "Kinh nghiệm lập trình tối thiểu 1 năm",
                ]
            ),
            "what_you_will_learn": json.dumps(
                [
                    "Thuật toán quy hoạch động nâng cao",
                    "Thuật toán tham lam và ứng dụng",
                    "Các thuật toán trên đồ thị",
                    "Kỹ thuật tối ưu hóa thuật toán",
                ]
            ),
            "learning_path": json.dumps(
                {
                    "units": [
                        {
                            "id": 1,
                            "title": "Quy hoạch động nâng cao",
                            "lessons": [
                                {
                                    "id": 1,
                                    "title": "Bài toán dãy con tăng dài nhất",
                                    "duration": 40,
                                },
                                {
                                    "id": 2,
                                    "title": "Bài toán cắt thanh",
                                    "duration": 35,
                                },
                            ],
                        },
                        {
                            "id": 2,
                            "title": "Thuật toán đồ thị",
                            "lessons": [
                                {
                                    "id": 3,
                                    "title": "Thuật toán Dijkstra",
                                    "duration": 45,
                                },
                                {
                                    "id": 4,
                                    "title": "Thuật toán Bellman-Ford",
                                    "duration": 50,
                                },
                            ],
                        },
                    ]
                }
            ),
        },
        {
            "title": "Chuẩn bị phỏng vấn kỹ thuật",
            "description": "Khóa học giúp bạn chuẩn bị cho các cuộc phỏng vấn kỹ thuật tại các công ty công nghệ lớn",
            "thumbnail_url": "https://example.com/thumbnails/interview-prep.jpg",
            "level": "Intermediate",
            "duration": 720,  # 12 giờ
            "price": 29.99,
            "is_published": True,
            "tags": "interview,coding,problem-solving",
            "requirements": json.dumps(
                [
                    "Kiến thức cơ bản về cấu trúc dữ liệu và thuật toán",
                    "Kỹ năng lập trình thành thạo một ngôn ngữ",
                ]
            ),
            "what_you_will_learn": json.dumps(
                [
                    "Giải quyết các bài toán phỏng vấn phổ biến",
                    "Kỹ thuật tối ưu hóa giải pháp",
                    "Cách trình bày ý tưởng rõ ràng",
                    "Chiến lược phỏng vấn hiệu quả",
                ]
            ),
            "learning_path": json.dumps(
                {
                    "units": [
                        {
                            "id": 1,
                            "title": "Chuẩn bị cơ bản",
                            "lessons": [
                                {
                                    "id": 1,
                                    "title": "Quy trình phỏng vấn",
                                    "duration": 20,
                                },
                                {
                                    "id": 2,
                                    "title": "Phương pháp giải quyết vấn đề",
                                    "duration": 30,
                                },
                            ],
                        },
                        {
                            "id": 2,
                            "title": "Bài tập phỏng vấn",
                            "lessons": [
                                {
                                    "id": 3,
                                    "title": "Bài tập về mảng và chuỗi",
                                    "duration": 40,
                                },
                                {
                                    "id": 4,
                                    "title": "Bài tập về cây và đồ thị",
                                    "duration": 45,
                                },
                            ],
                        },
                    ]
                }
            ),
        },
    ]

    db = SessionLocal()
    courses = []

    try:
        for course_data in courses_data:
            course = Course(**course_data)
            db.add(course)
            courses.append(course)

        db.commit()
        for course in courses:
            db.refresh(course)

        logger.info(f"Đã tạo {len(courses)} courses")
        return courses
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi tạo courses: {str(e)}")
        return []
    finally:
        db.close()


def create_users(badges: List[Badge], courses: List[Course]) -> List[User]:
    """
    Tạo dữ liệu mẫu cho bảng users và các bảng liên quan

    Args:
        badges (List[Badge]): Danh sách badges để gán cho users
        courses (List[Course]): Danh sách courses để tạo learning_progress

    Returns:
        List[User]: Danh sách các user đã tạo
    """
    logger.info("Tạo dữ liệu mẫu cho Users...")

    users_data = [
        {
            "email": "admin@example.com",
            "username": "admin",
            "hashed_password": pwd_context.hash("admin123"),
            "first_name": "Admin",
            "last_name": "User",
            "bio": "Quản trị viên hệ thống",
            "avatar": "https://example.com/avatars/admin.jpg",
        },
        {
            "email": "user1@example.com",
            "username": "user1",
            "hashed_password": pwd_context.hash("user123"),
            "first_name": "Nguyễn",
            "last_name": "Văn A",
            "bio": "Sinh viên năm nhất ngành Khoa học máy tính",
            "avatar": "https://example.com/avatars/user1.jpg",
        },
        {
            "email": "user2@example.com",
            "username": "user2",
            "hashed_password": pwd_context.hash("user123"),
            "first_name": "Trần",
            "last_name": "Thị B",
            "bio": "Kỹ sư phần mềm với 2 năm kinh nghiệm",
            "avatar": "https://example.com/avatars/user2.jpg",
        },
    ]

    db = SessionLocal()
    users = []

    try:
        # Tạo users
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
            db.flush()  # Để lấy ID của user mới tạo

            # Tạo user_state cho mỗi user
            user_state = UserState(
                user_id=user.id,
                last_active=datetime.now(),
                streak_count=random.randint(1, 30),
                total_points=random.randint(100, 1000),
                level=random.randint(1, 10),
                daily_goal=30,
                daily_progress=random.randint(0, 30),
                completed_exercises=random.randint(0, 20),
                completed_courses=random.randint(0, 3),
                problems_solved=random.randint(0, 50),
                algorithms_progress=random.randint(0, 100),
                data_structures_progress=random.randint(0, 100),
                dynamic_programming_progress=random.randint(0, 100),
            )
            db.add(user_state)

            users.append(user)

        db.commit()
        for user in users:
            db.refresh(user)

        logger.info(f"Đã tạo {len(users)} users và dữ liệu liên quan")
        return users
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi tạo users: {str(e)}")
        return []
    finally:
        db.close()


def seed_all():
    """
    Tạo tất cả dữ liệu mẫu cho ứng dụng
    """
    logger.info("Bắt đầu tạo dữ liệu mẫu...")

    # Tạo dữ liệu theo thứ tự phù hợp để tránh lỗi khóa ngoại
    topics = create_topics()
    if not topics:
        logger.error("Không thể tạo topics, dừng quá trình seed")
        return

    badges = create_badges()
    courses = create_courses()

    # Tạo dữ liệu liên quan
    create_exercises(topics)
    create_tests(topics)
    create_users(badges, courses)

    logger.info("Hoàn thành tạo dữ liệu mẫu!")


if __name__ == "__main__":
    seed_all()
