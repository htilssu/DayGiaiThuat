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

## Cấu hình

1. Tạo file `.env` trong thư mục server với nội dung sau:

```env
JWT_SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

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
├── routes/             # Chứa các route của API
├── models/            # Chứa các model dữ liệu
├── schemas/           # Chứa các schema Pydantic
└── utils/            # Chứa các utility function
```

## Lưu ý

- Đảm bảo đã kích hoạt môi trường ảo trước khi chạy server
- Kiểm tra file `.env` đã được cấu hình đúng
- Đảm bảo cổng 8000 không bị sử dụng bởi ứng dụng khác
- Cần có kết nối internet để load giao diện Swagger UI và ReDoc
