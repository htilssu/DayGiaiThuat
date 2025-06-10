# Tests cho Server API

Thư mục này chứa tất cả các test cho ứng dụng FastAPI.

## Cấu trúc

```
tests/
├── __init__.py         # Package init
├── conftest.py         # Fixtures cho pytest
├── test_auth.py        # Tests cho API xác thực
├── test_users.py       # Tests cho API người dùng
├── test_courses.py     # Tests cho API khóa học
└── test_utils.py       # Tests cho utility functions
```

## Cách chạy tests

### Chuẩn bị môi trường test

1. Đảm bảo đã cài đặt các dependencies:

```bash
pip install -r requirements.txt
```

2. Cấu hình biến môi trường cho test (hoặc sử dụng file .env):

```bash
export TEST_DB_USER=postgres
export TEST_DB_PASSWORD=postgres
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5432
export TEST_DB_NAME=test_db
export SECRET_KEY=your_secret_key_for_testing
```

### Chạy tất cả tests

```bash
pytest
```

### Chạy một file test cụ thể

```bash
pytest tests/test_auth.py
```

### Chạy một test cụ thể

```bash
pytest tests/test_auth.py::test_login_success
```

### Chạy test với báo cáo chi tiết

```bash
pytest -v
```

### Chạy test với báo cáo coverage

```bash
pytest --cov=app tests/
```

## Fixtures

Các fixtures được định nghĩa trong file `conftest.py` và có thể sử dụng trong tất cả các test:

- `setup_test_db`: Thiết lập database cho test
- `db`: Cung cấp session database cho mỗi test
- `client`: TestClient cho FastAPI app
- `test_user`: User thường để test
- `test_superuser`: User với quyền admin để test
- `token`: Token JWT cho test_user
- `superuser_token`: Token JWT cho test_superuser
- `authorized_client`: TestClient với token của test_user
- `superuser_client`: TestClient với token của test_superuser

## Thêm test mới

Khi thêm test mới, hãy tuân thủ các quy tắc sau:

1. Đặt tên file test với tiền tố `test_`
2. Đặt tên function test với tiền tố `test_`
3. Sử dụng docstring để mô tả mục đích của test
4. Sử dụng fixtures khi cần
5. Mỗi test nên kiểm tra một chức năng cụ thể 