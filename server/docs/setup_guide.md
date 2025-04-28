# Hướng Dẫn Cài Đặt và Khởi Tạo Dữ Liệu

Tài liệu này cung cấp hướng dẫn chi tiết về cách cài đặt ứng dụng và khởi tạo dữ liệu mẫu.

## Giới Thiệu

Hệ thống cung cấp các script để tự động hóa quá trình cài đặt và tạo dữ liệu mẫu:

1. **Setup Script**: Cài đặt môi trường, tạo cấu trúc thư mục, chạy migrations và tùy chọn chạy seeder
2. **Seeder Script**: Khởi tạo dữ liệu mẫu cho ứng dụng

## Yêu Cầu Hệ Thống

- Python 3.8+
- Pip (Trình quản lý package của Python)
- Cơ sở dữ liệu đã được cấu hình

## Cài Đặt Ứng Dụng

### Sử Dụng Setup Script

Script setup tự động hóa quá trình cài đặt và cấu hình ứng dụng. Các bước được thực hiện bao gồm:

1. Tạo các thư mục cần thiết
2. Cài đặt các dependencies từ requirements.txt
3. Chạy migrations để cập nhật cơ sở dữ liệu
4. Tùy chọn chạy seeder để tạo dữ liệu mẫu

#### Các Tham Số

Script chấp nhận các tham số sau:

- `--no-deps`: Bỏ qua việc cài đặt dependencies
- `--no-migrations`: Bỏ qua việc chạy migrations
- `--seed`: Chạy seeder để tạo dữ liệu mẫu

#### Cách Sử Dụng

```bash
# Đi đến thư mục gốc của server
cd server

# Cài đặt đầy đủ với dữ liệu mẫu
python scripts/setup.py --seed

# Cài đặt không có dữ liệu mẫu
python scripts/setup.py

# Chỉ chạy migrations và seeder, bỏ qua cài đặt dependencies
python scripts/setup.py --no-deps --seed

# Chỉ tạo thư mục và cài đặt dependencies, bỏ qua migrations
python scripts/setup.py --no-migrations
```

## Tạo Dữ Liệu Mẫu (Seeding)

Nếu bạn chỉ muốn tạo dữ liệu mẫu mà không cần chạy toàn bộ quá trình cài đặt, bạn có thể sử dụng script seeder riêng biệt.

### Sử Dụng Seeder Script

```bash
# Đi đến thư mục gốc của server
cd server

# Chạy seeder
python scripts/run_seeder.py
```

Script này sẽ tạo dữ liệu mẫu cho các entity sau:

- Users (Người dùng)
- Courses (Khóa học)
- Badges (Huy hiệu)
- User States (Trạng thái người dùng)
- Learning Progress (Tiến độ học tập)
- User Badges (Huy hiệu người dùng)

## Xử Lý Sự Cố

### Lỗi Cài Đặt Dependencies

Nếu gặp lỗi khi cài đặt dependencies:

1. Kiểm tra kết nối internet
2. Đảm bảo file requirements.txt tồn tại và chứa thông tin chính xác
3. Thử cài đặt thủ công: `pip install -r requirements.txt`

### Lỗi Migrations

Nếu gặp lỗi khi chạy migrations:

1. Kiểm tra kết nối đến cơ sở dữ liệu
2. Đảm bảo cấu hình cơ sở dữ liệu chính xác
3. Xem logs để biết thêm chi tiết về lỗi

### Lỗi Seeding

Nếu gặp lỗi khi chạy seeder:

1. Đảm bảo migrations đã được chạy thành công
2. Kiểm tra quyền truy cập cơ sở dữ liệu
3. Xem file logs/app.log để biết thêm chi tiết

## Tùy Chỉnh Dữ Liệu Mẫu

Nếu bạn muốn tùy chỉnh dữ liệu mẫu, bạn có thể chỉnh sửa các file seeder tương ứng trong thư mục `app/database/seeders/`.

Ví dụ:

- `user_seeder.py`: Tùy chỉnh dữ liệu người dùng mẫu
- `course_seeder.py`: Tùy chỉnh dữ liệu khóa học mẫu
- `badge_seeder.py`: Tùy chỉnh dữ liệu huy hiệu mẫu

Sau khi chỉnh sửa, bạn có thể chạy lại script seeder để cập nhật dữ liệu mẫu.
