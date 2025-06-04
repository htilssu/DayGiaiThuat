# Hướng dẫn Cài đặt và Chạy Server

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Python package manager)

## Các bước cài đặt

1. Tạo môi trường ảo Python (Virtual Environment)

```bash
python -m venv .venv
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

## Database Migration

Dự án sử dụng Alembic để quản lý migration database.

1. Tạo migration mới khi thay đổi model:

```bash
alembic revision --autogenerate -m "Mô tả thay đổi"
```

2. Áp dụng migration để cập nhật cơ sở dữ liệu:

```bash
alembic upgrade head
```

3. Xem lịch sử migration:

```bash
alembic history
```

4. Quay về version trước đó:

```bash
alembic downgrade -1
```

5. Tạo dữ liệu mẫu (seed data) sau khi migration:

```bash
# Cách 1: Sử dụng script riêng để chạy seeder
python scripts/run_seeder.py

# Hoặc cách 2: Sử dụng setup script với flag --seed
python scripts/setup.py --seed

# Hoặc cách 3: Sử dụng import trực tiếp (không khuyến khích)
python -c "from app.database.seeder import run_seeder; run_seeder()"
```

## Chạy server

1. Kích hoạt môi trường ảo (nếu chưa kích hoạt)

2. Chạy server bằng lệnh:

```bash
fastapi run main.py
```

Server sẽ chạy tại địa chỉ: http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Cấu trúc thư mục

```
server/
├── main.py                # File chính để chạy server
├── requirements.txt       # Danh sách các thư viện cần thiết
├── .env.example           # File mẫu cho cấu hình môi trường
├── alembic/               # Thư mục chứa cấu hình và các version migration
│   └── versions/          # Chứa các file migration đã tạo
├── app/                   # Thư mục chính của ứng dụng
│   ├── core/              # Chứa các module core của ứng dụng
│   │   └── agents/        # Chứa các agent và thành phần liên quan
│   │       └── components/# Thành phần của các agent
│   ├── crud/              # Chứa các hàm CRUD (Create, Read, Update, Delete)
│   ├── database/          # Chứa các module liên quan đến database
│   │   └── seeders/       # Các module seed dữ liệu cho từng model
│   ├── db/                # Cấu hình và kết nối database
│   ├── exceptions/        # Định nghĩa các exception tùy chỉnh
│   ├── middleware/        # Middleware của ứng dụng
│   ├── models/            # Chứa các model dữ liệu (SQLAlchemy)
│   ├── routers/           # Chứa các route của API
│   ├── schemas/           # Chứa các schema Pydantic
│   ├── services/          # Chứa các service xử lý logic nghiệp vụ
│   └── utils/             # Chứa các utility function
│       └── oauth2/        # Các hàm tiện ích liên quan đến OAuth2
├── docs/                  # Tài liệu hướng dẫn
├── static/                # Tài nguyên tĩnh
└── volumes/               # Thư mục chứa dữ liệu
```

## Lưu ý

- Đảm bảo đã kích hoạt môi trường ảo trước khi chạy server
- Kiểm tra file `.env` đã được cấu hình đúng và đầy đủ
- Đảm bảo cổng 8000 không bị sử dụng bởi ứng dụng khác
- Cần có kết nối internet để load giao diện Swagger UI và ReDoc
- KHÔNG commit file `.env` lên git repository (đã được thêm vào .gitignore)
