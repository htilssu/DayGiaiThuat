# Hướng dẫn Cài đặt và Chạy Server

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Python package manager)

## Các bước cài đặt

1. Tạo môi trường ảo Python (Virtual Environment)

```bash
python -m venv venv
```

2. Kích hoạt môi trường ảo

- Windows:

```bash
.\venv\Scripts\activate
```

- Linux/Mac:

```bash
source venv/bin/activate
```

3. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

## Cấu hình môi trường

1. Sao chép file `.env.example` thành file `.env`:

- Windows:

```bash
copy .env.example .env
```

- Linux/Mac:

```bash
cp .env.example .env
```

2. Chỉnh sửa các giá trị trong file `.env`:

- `JWT_SECRET_KEY`: Khóa bí mật để tạo JWT token (nên là một chuỗi ngẫu nhiên phức tạp)
- `DATABASE_URL`: URL kết nối đến database
- `BACKEND_CORS_ORIGINS`: Danh sách các domain được phép truy cập API
- Các cấu hình khác tùy theo nhu cầu

## Chạy server

1. Kích hoạt môi trường ảo (nếu chưa kích hoạt)

2. Chạy server bằng lệnh:

```bash
python main.py
```

Server sẽ chạy tại địa chỉ: http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Cấu trúc thư mục

```
server/
├── main.py              # File chính để chạy server
├── requirements.txt     # Danh sách các thư viện cần thiết
├── .env.example        # File mẫu cho cấu hình môi trường
├── routes/             # Chứa các route của API
├── models/            # Chứa các model dữ liệu
├── schemas/           # Chứa các schema Pydantic
└── utils/            # Chứa các utility function
```

## Lưu ý

- Đảm bảo đã kích hoạt môi trường ảo trước khi chạy server
- Kiểm tra file `.env` đã được cấu hình đúng và đầy đủ
- Đảm bảo cổng 8000 không bị sử dụng bởi ứng dụng khác
- Cần có kết nối internet để load giao diện Swagger UI và ReDoc
- KHÔNG commit file `.env` lên git repository (đã được thêm vào .gitignore)
