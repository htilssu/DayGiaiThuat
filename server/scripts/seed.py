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
from app.models.exercise_test_case_model import ExerciseTestCase
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

    # Seed exercises based on web/src/data/mockExercises.ts
    exercises_data = [
        {
            "title": "Tìm kiếm nhị phân",
            "description": "Cài đặt thuật toán tìm kiếm nhị phân và phân tích độ phức tạp",
            "difficulty": "Beginner",
            "category": "Tìm kiếm",
            "estimated_time": "30 phút",
            "completion_rate": 78,
            "completed": True,
            "content": "# Tìm kiếm nhị phân...",
            "code_template": "def binary_search(arr, target):\n    pass",
        },
        {
            "title": "Sắp xếp nhanh (Quick Sort)",
            "description": "Cài đặt thuật toán sắp xếp nhanh với phân hoạch Lomuto",
            "difficulty": "Intermediate",
            "category": "Sắp xếp",
            "estimated_time": "45 phút",
            "completion_rate": 65,
            "completed": False,
            "content": "# Sắp xếp nhanh...",
            "code_template": "def quick_sort(arr):\n    pass",
        },
        {
            "title": "Cây nhị phân tìm kiếm",
            "description": "Cài đặt cấu trúc dữ liệu cây nhị phân tìm kiếm với các thao tác cơ bản",
            "difficulty": "Intermediate",
            "category": "Cấu trúc dữ liệu",
            "estimated_time": "60 phút",
            "completion_rate": 52,
            "completed": False,
            "content": "# BST...",
            "code_template": "class Node: ...",
        },
        {
            "title": "Thuật toán Dijkstra",
            "description": "Tìm đường đi ngắn nhất trên đồ thị có trọng số không âm",
            "difficulty": "Advanced",
            "category": "Đồ thị",
            "estimated_time": "90 phút",
            "completion_rate": 42,
            "completed": False,
            "content": "# Dijkstra...",
            "code_template": "def dijkstra(graph, start):\n    pass",
        },
        {
            "title": "Quy hoạch động - Dãy con tăng dài nhất",
            "description": "Giải quyết bài toán tìm dãy con tăng dài nhất bằng quy hoạch động",
            "difficulty": "Advanced",
            "category": "Quy hoạch động",
            "estimated_time": "75 phút",
            "completion_rate": 38,
            "completed": False,
            "content": "# LIS...",
            "code_template": "def length_of_lis(nums):\n    pass",
        },
        {
            "title": "Số Fibonacci",
            "description": "Cài đặt các phương pháp tính số Fibonacci và so sánh hiệu suất",
            "difficulty": "Beginner",
            "category": "Đệ quy",
            "estimated_time": "30 phút",
            "completion_rate": 85,
            "completed": True,
            "content": "# Fibonacci...",
            "code_template": "def fibonacci(n):\n    pass",
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


def create_exercise_test_cases(exercises: List[Exercise]) -> int:
    """
    Tạo test cases mẫu cho mỗi bài tập (3 test cases/bài).

    Args:
        exercises (List[Exercise]): Danh sách bài tập đã tạo

    Returns:
        int: Tổng số test cases đã tạo
    """
    logger.info("Tạo dữ liệu mẫu cho Exercise Test Cases dựa trên nội dung bài tập...")

    if not exercises:
        logger.warning("Không có bài tập nào để tạo test cases")
        return 0

    db = SessionLocal()
    created = 0

    try:
        for ex in exercises:
            name = ex.title.lower()
            test_cases: List[dict] = []

            if "tìm kiếm nhị phân" in name or "binary" in name:
                # 10 cases: arrays and targets -> index or -1. Input as JSON array of args: [[arr], target]
                cases = [
                    (([1, 3, 5, 7, 9, 11, 13, 15], 7), "3"),
                    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1), "0"),
                    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10), "9"),
                    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 11), "-1"),
                    (([0, 5, 10, 15, 20, 25, 30], 0), "0"),
                    (([0, 5, 10, 15, 20, 25, 30], 25), "5"),
                    (([0, 5, 10, 15, 20, 25, 30], -5), "-1"),
                    (([2, 4, 6, 8, 10, 12], 6), "2"),
                    (([2, 4, 6, 8, 10, 12], 5), "-1"),
                    (([100, 200, 300, 400, 500], 500), "4"),
                ]
                for (args, out) in cases:
                    test_cases.append({
                        "input_data": json.dumps([list(args[0]), args[1]]),
                        "output_data": out,
                        "explain": "Binary search expected index"
                    })

            elif "sắp xếp nhanh" in name or "quick" in name:
                arrays = [
                    [9, 7, 5, 11, 12, 2, 14, 3, 10, 6],
                    [5, 4, 3, 2, 1],
                    [1, 1, 1, 1, 1],
                    [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
                    [],
                    [0],
                    [-1, -3, -2, 0, 2, 1],
                    [10, -1, 2, -10, 5, 0],
                    [100, 50, 100, 50, 25],
                    [2, 2, 2, 1, 1, 3, 3, 0],
                ]
                for arr in arrays:
                    sorted_arr = sorted(arr)
                    test_cases.append({
                        "input_data": json.dumps([arr]),  # [[...]] so it becomes fn(arr)
                        "output_data": json.dumps(sorted_arr),
                        "explain": "Quick sort expected sorted array",
                    })

            elif "dãy con tăng dài nhất" in name or "lis" in name:
                arrays = [
                    [10, 9, 2, 5, 3, 7, 101, 18],
                    [0, 1, 0, 3, 2, 3],
                    [7, 7, 7, 7, 7, 7, 7],
                    [1, 3, 6, 7, 9, 4, 10, 5, 6],
                    [1, 2, 3, 4, 5, 6, 7, 8, 9],
                    [9, 8, 7, 6, 5, 4, 3, 2, 1],
                    [3, 10, 2, 1, 20],
                    [50, 3, 10, 7, 40, 80],
                    [2],
                    [],
                ]
                # Compute LIS length straightforwardly here for expected

                def lis_len(nums: List[int]) -> int:
                    if not nums:
                        return 0
                    dp = []
                    import bisect
                    for x in nums:
                        i = bisect.bisect_left(dp, x)
                        if i == len(dp):
                            dp.append(x)
                        else:
                            dp[i] = x
                    return len(dp)

                for arr in arrays:
                    test_cases.append({
                        "input_data": json.dumps([arr]),
                        "output_data": str(lis_len(arr)),
                        "explain": "Length of LIS",
                    })

            elif "fibonacci" in name:
                ns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]

                def fib(n: int) -> int:
                    a, b = 0, 1
                    for _ in range(n):
                        a, b = b, a + b
                    return a
                for n in ns:
                    test_cases.append({
                        "input_data": json.dumps([n]),
                        "output_data": str(fib(n)),
                        "explain": "Fibonacci number",
                    })

            elif "dijkstra" in name:
                graphs = [
                    ({"0": [[1, 2], [2, 4]], "1": [[2, 1]], "2": []}, 0, {"0": 0, "1": 2, "2": 3}),
                    ({"0": [[1, 1]], "1": [[2, 2]], "2": [[0, 4]]}, 0, {"0": 0, "1": 1, "2": 3}),
                    ({"0": [[1, 5], [2, 2]], "1": [[2, 1]], "2": [[1, 1]]}, 0, {"0": 0, "1": 3, "2": 2}),
                    ({"0": [[1, 10]], "1": [], "2": []}, 0, {"0": 0, "1": 10, "2": None}),
                    ({"0": [[1, 3], [3, 7]], "1": [[2, 4]], "2": [[3, 1]], "3": []}, 0, {"0": 0, "1": 3, "2": 7, "3": 8}),
                ]
                # Duplicate to reach 10 by reusing first five with slight variations on start
                graphs = graphs + graphs
                for g, start, dist in graphs[:10]:
                    # Replace None distances with a large value or string if desired; keep None -> null
                    test_cases.append({
                        "input_data": json.dumps([g, start]),
                        "output_data": json.dumps(dist),
                        "explain": "Shortest path distances from start",
                    })

            elif "cây nhị phân tìm kiếm" in name or "bst" in name:
                scenarios = [
                    (["insert", [5, 3, 7, 2, 4, 6, 8], "search", 4], "True"),
                    (["insert", [5, 3, 7, 2, 4, 6, 8], "search", 10], "False"),
                    (["insert", [10, 5, 15, 3, 7, 12, 18], "search", 12], "True"),
                    (["insert", [10, 5, 15, 3, 7, 12, 18], "search", 11], "False"),
                    (["insert", [2, 1, 3], "search", 1], "True"),
                    (["insert", [2, 1, 3], "search", 4], "False"),
                    (["insert", [8, 3, 10, 1, 6, 14, 4, 7, 13], "search", 7], "True"),
                    (["insert", [8, 3, 10, 1, 6, 14, 4, 7, 13], "search", 2], "False"),
                    (["insert", [1], "search", 1], "True"),
                    (["insert", [], "search", 1], "False"),
                ]
                for args, out in scenarios:
                    test_cases.append({
                        "input_data": json.dumps(args),
                        "output_data": out,
                        "explain": "BST operations result",
                    })

            else:
                # Fallback: simple arithmetic placeholder to reach 10 cases
                for a, b in [
                    (1, 2),
                    (2, 3),
                    (3, 5),
                    (5, 8),
                    (8, 13),
                    (13, 21),
                    (21, 34),
                    (34, 55),
                    (55, 89),
                    (89, 144),
                ]:
                    test_cases.append({
                        "input_data": json.dumps([a, b]),
                        "output_data": str(a + b),
                        "explain": "Placeholder test case",
                    })

            # Persist up to 10 test cases per exercise
            for tc in test_cases[:10]:
                db.add(
                    ExerciseTestCase(
                        exercise_id=ex.id,
                        input_data=tc["input_data"],
                        output_data=tc["output_data"],
                        explain=tc.get("explain"),
                    )
                )
                created += 1

        db.commit()
        logger.info(f"Đã tạo {created} exercise test cases")
        return created
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi tạo exercise test cases: {str(e)}")
        return 0
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
        {"topic_id": 1, "duration_minutes": 60},
        {"topic_id": 2, "duration_minutes": 60},
        {"topic_id": 3, "duration_minutes": 60},
        {"topic_id": 4, "duration_minutes": 60},
        {"topic_id": 5, "duration_minutes": 60},
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
            # Course model stores serialized fields as strings; omit extra JSON fields not in model
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
            # omit learning_path (not a column)
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
            # omit learning_path (not a column)
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
            "is_admin": True,
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

    # badges = create_badges()
    # courses = create_courses()

    # Tạo dữ liệu liên quan
    exercises = create_exercises(topics)
    create_exercise_test_cases(exercises)
    # create_tests(topics)
    # create_users(badges, courses)

    logger.info("Hoàn thành tạo dữ liệu mẫu!")


if __name__ == "__main__":
    seed_all()
