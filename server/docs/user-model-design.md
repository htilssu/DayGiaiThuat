# Thiết kế Model User mới

## Tổng quan

Thiết kế mới kết hợp các thông tin từ cả `User` và `Profile` vào một bảng duy nhất `users` trong PostgreSQL. Thiết kế này giúp:

1. Đơn giản hóa cấu trúc cơ sở dữ liệu
2. Giảm số lượng truy vấn cần thiết để lấy thông tin người dùng
3. Tránh việc phải đồng bộ dữ liệu giữa hai hệ thống cơ sở dữ liệu khác nhau (PostgreSQL và MongoDB)

## Cấu trúc Model User

### Các trường cơ bản

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Các trường thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Các trường từ Profile

```python
    # Các trường từ ProfileBase
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    # Các trường JSON để lưu trữ dữ liệu phức tạp
    stats = Column(JSON, default=lambda: {...})
    badges = Column(JSON, default=lambda: [...])
    activities = Column(JSON, default=list)
    learning_progress = Column(JSON, default=lambda: {...})
    courses = Column(JSON, default=list)
```

## Sử dụng JSON Column

PostgreSQL hỗ trợ lưu trữ dữ liệu JSON một cách native, cho phép chúng ta lưu trữ các cấu trúc dữ liệu phức tạp như danh sách và từ điển trong một cột duy nhất. Điều này rất hữu ích để lưu trữ các thông tin như:

1. **stats**: Các số liệu thống kê của người dùng (completed_exercises, completed_courses, total_points, streak_days, level, problems_solved)
2. **badges**: Danh sách các huy hiệu người dùng đã đạt được
3. **activities**: Lịch sử hoạt động của người dùng
4. **learning_progress**: Tiến độ học tập của người dùng trong các lĩnh vực khác nhau
5. **courses**: Danh sách các khóa học người dùng đang theo dõi và tiến độ của họ

## Ưu điểm của thiết kế mới

1. **Hiệu suất**: Giảm số lượng truy vấn cần thiết để lấy thông tin đầy đủ của người dùng (từ 2 truy vấn xuống 1 truy vấn)
2. **Tính nhất quán**: Tất cả dữ liệu người dùng được lưu trữ trong một bảng, giảm thiểu khả năng mất đồng bộ dữ liệu
3. **Đơn giản hóa code**: Không cần phải xử lý hai loại cơ sở dữ liệu khác nhau, giảm độ phức tạp của code
4. **Dễ bảo trì**: Một model duy nhất để quản lý, giảm thiểu việc phải cập nhật nhiều nơi khi có thay đổi
5. **Linh hoạt**: JSON column cho phép mở rộng cấu trúc dữ liệu mà không cần phải thay đổi schema của bảng

## Nhược điểm và cách khắc phục

1. **Tìm kiếm trong JSON**: Tìm kiếm trong cột JSON có thể chậm hơn so với các cột thông thường. Khắc phục: Sử dụng các index tối ưu cho JSON nếu cần tìm kiếm thường xuyên.

2. **Giới hạn kích thước**: Cột JSON có giới hạn kích thước, đặc biệt là đối với danh sách activities có thể tăng lên theo thời gian. Khắc phục: Có thể giới hạn số lượng activities được lưu trữ hoặc định kỳ xóa các activities cũ.

3. **Tính nguyên tử**: Khó đảm bảo tính nguyên tử khi cập nhật một phần của cột JSON. Khắc phục: Thiết kế các hàm cập nhật đơn giản, rõ ràng và xử lý lỗi cẩn thận.

## Hướng dẫn sử dụng

### Truy vấn dữ liệu

```python
# Lấy thông tin cơ bản
user = db.query(User).filter(User.id == user_id).first()

# Truy cập các trường JSON
stats = user.stats
badges = user.badges
activities = user.activities
```

### Cập nhật dữ liệu

```python
# Cập nhật một thống kê
user.stats["completed_exercises"] += 1

# Thêm một huy hiệu mới
user.badges.append({
    "id": 5,
    "name": "Huy hiệu mới",
    "icon": "🏆",
    "description": "Mô tả huy hiệu",
    "unlocked": True
})

# Lưu vào database
db.commit()
```

## Kết luận

Thiết kế mới của model User kết hợp dữ liệu từ cả User và Profile vào một bảng duy nhất, giúp đơn giản hóa cấu trúc cơ sở dữ liệu, tăng hiệu suất và dễ bảo trì. Việc sử dụng JSON column trong PostgreSQL cho phép lưu trữ các cấu trúc dữ liệu phức tạp mà không làm phức tạp schema của bảng.
