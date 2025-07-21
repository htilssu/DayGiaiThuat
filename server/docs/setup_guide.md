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

## Cấu hình Cloudflare R2 cho File Storage

Ứng dụng hỗ trợ sử dụng Cloudflare R2 để lưu trữ files (ảnh khóa học, avatar người dùng). R2 sử dụng S3-compatible API nên có thể dễ dàng tích hợp.

### 1. Tạo R2 Bucket

1. Đăng nhập vào Cloudflare Dashboard
2. Chọn **R2 Object Storage** từ sidebar
3. Tạo bucket mới với tên tùy ý (ví dụ: `giaithuat-storage`)
4. Cấu hình bucket settings theo nhu cầu

### 2. Cấu hình Public Access

**Quan trọng**: Để ảnh có thể hiển thị trên web, bạn cần cấu hình public access cho bucket:

1. Trong bucket settings, chọn **Settings** tab
2. Tìm section **Public access**
3. Bật **Allow public access** hoặc cấu hình **Custom domain**

**Lưu ý**: Nếu không cấu hình public access, ảnh sẽ upload thành công nhưng không thể truy cập từ web.

### 3. Cấu hình CORS (tuỳ chọn)

Để tránh lỗi CORS khi load ảnh từ frontend, thêm CORS policy:

```json
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3000
  }
]
```

### 4. Tạo API Token

1. Trong R2 dashboard, chọn **Manage R2 API tokens**
2. Tạo API token mới với quyền:
   - **Object Read & Write** cho bucket vừa tạo
3. Lưu lại `Access Key ID` và `Secret Access Key`

### 5. Lấy Account ID

1. Trong Cloudflare Dashboard, account ID được hiển thị ở sidebar phải
2. Endpoint URL sẽ có format: `https://[account-id].r2.cloudflarestorage.com`

### 6. Cấu hình Environment Variables

Thêm các biến sau vào file `.env`:

```env
# Cloudflare R2 Settings
S3_ACCESS_KEY_ID=your_r2_access_key_id_here
S3_SECRET_ACCESS_KEY=your_r2_secret_access_key_here
S3_REGION=auto
S3_BUCKET_NAME=your_r2_bucket_name_here
S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com

# Tuỳ chọn: URL public custom (nếu có)
S3_PUBLIC_URL=

# Prefixes cho file
S3_COURSE_IMAGE_PREFIX=course-images/
S3_USER_AVATAR_PREFIX=user-avatars/
```

### 7. Test Upload

Sau khi cấu hình xong:

1. Restart backend server
2. Thử upload ảnh khóa học từ admin panel
3. Kiểm tra URL response có đúng format không
4. Verify ảnh có hiển thị trên web không

### Troubleshooting

#### Ảnh upload thành công nhưng không hiển thị

1. **Kiểm tra Public Access**: Đảm bảo bucket đã bật public access
2. **Kiểm tra URL format**: URL phải có format `https://[bucket].r2.dev/[file-path]`
3. **Kiểm tra CORS**: Nếu có lỗi CORS, cần cấu hình CORS policy
4. **Restart frontend**: Next.js cần restart để áp dụng thay đổi cấu hình

#### Lỗi upload

1. **Kiểm tra credentials**: Access key và secret key đúng chưa
2. **Kiểm tra permissions**: Token có quyền write vào bucket không
3. **Kiểm tra endpoint URL**: Account ID trong URL đúng chưa

## Cấu hình Database

[Existing database setup content...]

## Cấu hình AI/LLM

[Existing AI setup content...]
