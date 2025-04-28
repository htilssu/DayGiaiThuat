"""
Module này chứa các hàm seeder cho model Course.
"""
import json
import logging
from sqlalchemy.orm import Session

from app.models.course import Course

# Tạo logger
logger = logging.getLogger(__name__)

# Dữ liệu mẫu cho courses
sample_courses = [
    # ----------------- Cấp độ Cơ bản -----------------
    {
        "title": "Thuật toán cơ bản",
        "description": "Khóa học giới thiệu về cơ bản của thuật toán, độ phức tạp và các kỹ thuật phân tích thuật toán cho người mới bắt đầu.",
        "thumbnail_url": "https://i.ibb.co/WnG0GQM/algo-intro.jpg",
        "level": "Cơ bản",
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
        ]),
        "learning_path": json.dumps({
            "units": [
                {
                    "title": "Giới thiệu về thuật toán",
                    "description": "Hiểu các khái niệm cơ bản về thuật toán và phương pháp tiếp cận",
                    "lessons": [
                        {"id": 1, "title": "Thuật toán là gì", "type": "theory", "xp": 10},
                        {"id": 2, "title": "Tại sao phải học thuật toán", "type": "theory", "xp": 10},
                        {"id": 3, "title": "Viết thuật toán đầu tiên", "type": "practice", "xp": 20},
                        {"id": 4, "title": "Kiểm tra kiến thức", "type": "quiz", "xp": 15}
                    ]
                },
                {
                    "title": "Độ phức tạp thuật toán",
                    "description": "Học cách phân tích hiệu năng của thuật toán",
                    "lessons": [
                        {"id": 5, "title": "Độ phức tạp thời gian", "type": "theory", "xp": 10},
                        {"id": 6, "title": "Ký hiệu Big-O", "type": "theory", "xp": 15},
                        {"id": 7, "title": "Bài tập phân tích", "type": "practice", "xp": 25},
                        {"id": 8, "title": "Kiểm tra độ phức tạp", "type": "quiz", "xp": 20}
                    ]
                },
                {
                    "title": "Thuật toán sắp xếp",
                    "description": "Tìm hiểu các thuật toán sắp xếp phổ biến",
                    "lessons": [
                        {"id": 9, "title": "Bubble Sort", "type": "theory", "xp": 10},
                        {"id": 10, "title": "Selection Sort", "type": "theory", "xp": 10},
                        {"id": 11, "title": "Insertion Sort", "type": "theory", "xp": 10},
                        {"id": 12, "title": "Thực hành sắp xếp", "type": "practice", "xp": 30},
                        {"id": 13, "title": "Kiểm tra thuật toán sắp xếp", "type": "quiz", "xp": 20}
                    ]
                },
                {
                    "title": "Thuật toán tìm kiếm",
                    "description": "Học các thuật toán tìm kiếm cơ bản",
                    "lessons": [
                        {"id": 14, "title": "Tìm kiếm tuyến tính", "type": "theory", "xp": 10},
                        {"id": 15, "title": "Tìm kiếm nhị phân", "type": "theory", "xp": 15},
                        {"id": 16, "title": "Bài tập thực hành", "type": "practice", "xp": 25},
                        {"id": 17, "title": "Kiểm tra cuối khóa", "type": "quiz", "xp": 25}
                    ]
                }
            ],
            "achievements": [
                {"id": "algo_basics", "title": "Nhà thuật toán tập sự", "description": "Hoàn thành khóa học cơ bản", "xp": 50},
                {"id": "sort_master", "title": "Bậc thầy sắp xếp", "description": "Đạt điểm tối đa trong bài kiểm tra sắp xếp", "xp": 30},
                {"id": "search_expert", "title": "Chuyên gia tìm kiếm", "description": "Giải quyết tất cả bài tập tìm kiếm", "xp": 30}
            ]
        })
    },
    
    # ----------------- Cấp độ Mới bắt đầu -----------------
    {
        "title": "Lập trình Python cho người mới",
        "description": "Khóa học toàn diện dạy Python từ cơ bản đến nâng cao, với trọng tâm là ứng dụng để giải quyết các bài toán thuật toán.",
        "thumbnail_url": "https://i.ibb.co/7r5h44P/python-basic.jpg",
        "level": "Mới bắt đầu",
        "duration": 900,  # 15 giờ
        "price": 149000.0,
        "is_published": True,
        "tags": "python,programming,beginner",
        "requirements": json.dumps(["Không yêu cầu kiến thức lập trình trước đó", "Máy tính cá nhân", "Sự kiên nhẫn và quyết tâm học tập"]),
        "what_you_will_learn": json.dumps([
            "Làm chủ cú pháp Python và các cấu trúc dữ liệu cơ bản",
            "Xây dựng các chương trình Python đơn giản",
            "Áp dụng Python để giải quyết các bài toán thuật toán cơ bản",
            "Sử dụng các thư viện Python phổ biến cho phân tích dữ liệu"
        ]),
        "learning_path": json.dumps({
            "units": [
                {
                    "title": "Giới thiệu Python",
                    "description": "Tổng quan về Python và cài đặt môi trường",
                    "lessons": [
                        {"id": 1, "title": "Python là gì và tại sao nên học", "type": "theory", "xp": 10},
                        {"id": 2, "title": "Cài đặt Python và môi trường phát triển", "type": "theory", "xp": 15},
                        {"id": 3, "title": "Chương trình Python đầu tiên", "type": "practice", "xp": 20},
                        {"id": 4, "title": "Thử thách học Python", "type": "quiz", "xp": 15}
                    ]
                },
                {
                    "title": "Cú pháp và biến",
                    "description": "Học cú pháp cơ bản và cách sử dụng biến trong Python",
                    "lessons": [
                        {"id": 5, "title": "Biến và kiểu dữ liệu", "type": "theory", "xp": 10},
                        {"id": 6, "title": "Toán tử trong Python", "type": "theory", "xp": 10},
                        {"id": 7, "title": "Nhập và xuất dữ liệu", "type": "theory", "xp": 10},
                        {"id": 8, "title": "Bài tập thực hành", "type": "practice", "xp": 25},
                        {"id": 9, "title": "Kiểm tra kiến thức", "type": "quiz", "xp": 20}
                    ]
                },
                {
                    "title": "Cấu trúc điều khiển",
                    "description": "Tìm hiểu về các cấu trúc điều khiển trong Python",
                    "lessons": [
                        {"id": 10, "title": "Câu lệnh điều kiện if-else", "type": "theory", "xp": 10},
                        {"id": 11, "title": "Vòng lặp for", "type": "theory", "xp": 10},
                        {"id": 12, "title": "Vòng lặp while", "type": "theory", "xp": 10},
                        {"id": 13, "title": "Lệnh break và continue", "type": "theory", "xp": 10},
                        {"id": 14, "title": "Bài tập thực hành", "type": "practice", "xp": 30},
                        {"id": 15, "title": "Kiểm tra cấu trúc điều khiển", "type": "quiz", "xp": 20}
                    ]
                },
                {
                    "title": "Hàm và Module",
                    "description": "Học cách tổ chức mã với hàm và module",
                    "lessons": [
                        {"id": 16, "title": "Định nghĩa và gọi hàm", "type": "theory", "xp": 15},
                        {"id": 17, "title": "Tham số và giá trị trả về", "type": "theory", "xp": 15},
                        {"id": 18, "title": "Module và package", "type": "theory", "xp": 15},
                        {"id": 19, "title": "Thực hành viết hàm", "type": "practice", "xp": 25},
                        {"id": 20, "title": "Kiểm tra cuối khóa", "type": "quiz", "xp": 25}
                    ]
                }
            ],
            "achievements": [
                {"id": "python_starter", "title": "Nhà phát triển Python tập sự", "description": "Hoàn thành khóa học Python cơ bản", "xp": 50},
                {"id": "code_writer", "title": "Tác giả mã nguồn", "description": "Viết 10 chương trình Python hoàn chỉnh", "xp": 40},
                {"id": "debug_hero", "title": "Anh hùng gỡ lỗi", "description": "Sửa thành công 5 lỗi trong các bài tập thực hành", "xp": 30}
            ]
        })
    },
    
    # ----------------- Cấp độ Lập trình thi đấu -----------------
    {
        "title": "Lập trình thi đấu toàn diện",
        "description": "Khóa học giúp bạn trở thành một lập trình viên thi đấu xuất sắc với các kỹ thuật và chiến lược tối ưu.",
        "thumbnail_url": "https://i.ibb.co/SfyKVKM/competitive-basic.jpg",
        "level": "Lập trình thi đấu",
        "duration": 1080,  # 18 giờ
        "price": 299000.0,
        "is_published": True,
        "tags": "competitive-programming,algorithms,data-structures,contest",
        "requirements": json.dumps([
            "Kiến thức lập trình cơ bản với C++, Java hoặc Python",
            "Hiểu biết về cấu trúc dữ liệu và thuật toán cơ bản",
            "Kiến thức toán học cơ bản (đại số, số học, tổ hợp)"
        ]),
        "what_you_will_learn": json.dumps([
            "Nắm vững các kỹ thuật tối ưu hóa thời gian và bộ nhớ",
            "Chiến lược giải quyết các bài toán trong thời gian giới hạn",
            "Sử dụng hiệu quả các thư viện chuẩn trong lập trình thi đấu",
            "Tiếp cận các bài toán từ Codeforces, LeetCode và các nền tảng thi đấu khác"
        ]),
        "learning_path": json.dumps({
            "units": [
                {
                    "title": "Giới thiệu về lập trình thi đấu",
                    "description": "Tổng quan về lập trình thi đấu và môi trường thi",
                    "lessons": [
                        {"id": 1, "title": "Lập trình thi đấu là gì", "type": "theory", "xp": 10},
                        {"id": 2, "title": "Các nền tảng thi đấu phổ biến", "type": "theory", "xp": 10},
                        {"id": 3, "title": "Chuẩn bị môi trường và công cụ", "type": "theory", "xp": 15},
                        {"id": 4, "title": "Bài tập làm quen", "type": "practice", "xp": 25},
                        {"id": 5, "title": "Kiểm tra kiến thức", "type": "quiz", "xp": 15}
                    ]
                },
                {
                    "title": "Tối ưu hóa thuật toán",
                    "description": "Các kỹ thuật tối ưu hóa thuật toán trong lập trình thi đấu",
                    "lessons": [
                        {"id": 6, "title": "Phân tích độ phức tạp nâng cao", "type": "theory", "xp": 15},
                        {"id": 7, "title": "Kỹ thuật tối ưu hóa thời gian", "type": "theory", "xp": 15},
                        {"id": 8, "title": "Kỹ thuật tối ưu hóa bộ nhớ", "type": "theory", "xp": 15},
                        {"id": 9, "title": "Bài tập tối ưu hóa", "type": "practice", "xp": 30},
                        {"id": 10, "title": "Kiểm tra tối ưu hóa", "type": "quiz", "xp": 20}
                    ]
                },
                {
                    "title": "Cấu trúc dữ liệu nâng cao",
                    "description": "Học các cấu trúc dữ liệu chuyên biệt cho lập trình thi đấu",
                    "lessons": [
                        {"id": 11, "title": "Segment Tree", "type": "theory", "xp": 20},
                        {"id": 12, "title": "Fenwick Tree (BIT)", "type": "theory", "xp": 20},
                        {"id": 13, "title": "Sparse Table", "type": "theory", "xp": 20},
                        {"id": 14, "title": "Disjoint Set Union (DSU)", "type": "theory", "xp": 20},
                        {"id": 15, "title": "Bài tập thực hành", "type": "practice", "xp": 40},
                        {"id": 16, "title": "Kiểm tra kiến thức", "type": "quiz", "xp": 25}
                    ]
                },
                {
                    "title": "Thuật toán đồ thị",
                    "description": "Các thuật toán đồ thị nâng cao cho lập trình thi đấu",
                    "lessons": [
                        {"id": 17, "title": "Đường đi ngắn nhất (Dijkstra, Bellman-Ford)", "type": "theory", "xp": 25},
                        {"id": 18, "title": "Cây khung nhỏ nhất (Kruskal, Prim)", "type": "theory", "xp": 20},
                        {"id": 19, "title": "Thuật toán tìm thành phần liên thông mạnh", "type": "theory", "xp": 20},
                        {"id": 20, "title": "Bài tập đồ thị", "type": "practice", "xp": 40},
                        {"id": 21, "title": "Kiểm tra thuật toán đồ thị", "type": "quiz", "xp": 25}
                    ]
                },
                {
                    "title": "Quy hoạch động",
                    "description": "Học các kỹ thuật quy hoạch động nâng cao",
                    "lessons": [
                        {"id": 22, "title": "Quy hoạch động 1D và 2D", "type": "theory", "xp": 20},
                        {"id": 23, "title": "Quy hoạch động bitmask", "type": "theory", "xp": 25},
                        {"id": 24, "title": "Quy hoạch động trên cây", "type": "theory", "xp": 25},
                        {"id": 25, "title": "Tối ưu hóa quy hoạch động", "type": "theory", "xp": 25},
                        {"id": 26, "title": "Bài tập thực hành", "type": "practice", "xp": 50},
                        {"id": 27, "title": "Kiểm tra cuối khóa", "type": "quiz", "xp": 30}
                    ]
                }
            ],
            "achievements": [
                {"id": "competitive_initiate", "title": "Người nhập môn lập trình thi đấu", "description": "Hoàn thành khóa học", "xp": 100},
                {"id": "problem_solver", "title": "Người giải quyết vấn đề", "description": "Giải 20 bài tập thực hành", "xp": 80},
                {"id": "time_optimizer", "title": "Bậc thầy tối ưu", "description": "Đạt điểm tối đa trong bài kiểm tra tối ưu hóa", "xp": 50},
                {"id": "graph_expert", "title": "Chuyên gia đồ thị", "description": "Giải quyết tất cả bài tập đồ thị", "xp": 50},
                {"id": "dp_master", "title": "Bậc thầy quy hoạch động", "description": "Đạt điểm tối đa trong bài kiểm tra quy hoạch động", "xp": 70}
            ]
        })
    }
]

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
            what_you_will_learn=course_data["what_you_will_learn"],
            learning_path=course_data["learning_path"]
        )
        db.add(course)
    
    db.commit()
    logger.info(f"Đã tạo {len(sample_courses)} khóa học mẫu.") 