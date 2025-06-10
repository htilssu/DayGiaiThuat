# Scripts Hỗ Trợ

Thư mục này chứa các script hỗ trợ cho ứng dụng.

## Seed Data

Script `seed.py` được sử dụng để tạo dữ liệu mẫu cho ứng dụng.

### Cách sử dụng

Có hai cách để chạy script seed:

1. **Chạy trực tiếp từ command line:**

```bash
# Chạy từ thư mục gốc của dự án
python -m scripts.seed
```

2. **Chạy tự động khi khởi động ứng dụng:**

Cấu hình các biến môi trường sau trong file `.env`:

```
RUN_SEEDERS_ON_STARTUP=True
SEEDERS_TO_RUN=["all"]  # hoặc danh sách các seeder cụ thể
FORCE_SEEDERS=False  # True để xóa dữ liệu cũ trước khi tạo mới
```

### Dữ liệu được tạo

Script seed sẽ tạo các dữ liệu mẫu sau:

- **Topics**: Các chủ đề học tập (Cấu trúc dữ liệu, Thuật toán sắp xếp, v.v.)
- **Exercises**: Các bài tập liên quan đến các chủ đề
- **Tests**: Các bài kiểm tra cho từng chủ đề
- **Badges**: Các huy hiệu thành tích
- **Courses**: Các khóa học với thông tin chi tiết
- **Users**: Người dùng mẫu với dữ liệu liên quan (UserState, LearningProgress, LearningPath)

## Các Script Khác

Các script khác có thể được thêm vào thư mục này để hỗ trợ các tác vụ khác nhau của ứng dụng.

## Lưu ý

- Các script này chỉ nên được sử dụng trong môi trường phát triển hoặc kiểm thử.
- Đảm bảo bạn hiểu rõ tác động của script trước khi chạy, đặc biệt là khi sử dụng tùy chọn `FORCE_SEEDERS=True`. 