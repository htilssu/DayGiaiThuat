"""
Tests cho các API endpoints trong auth router.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user_model import User


def test_login_success(client: TestClient, test_user: User):
    """Test đăng nhập thành công với thông tin đúng."""
    response = client.post(
        "/auth/login", data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user: User):
    """Test đăng nhập thất bại với mật khẩu sai."""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email hoặc mật khẩu không chính xác"


def test_login_nonexistent_user(client: TestClient):
    """Test đăng nhập thất bại với email không tồn tại."""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "password123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email hoặc mật khẩu không chính xác"


def test_get_current_user(authorized_client: TestClient, test_user: User):
    """Test lấy thông tin người dùng hiện tại với token hợp lệ."""
    response = authorized_client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["fullName"] == test_user.full_name
    assert "hashedPassword" not in data


def test_get_current_user_unauthorized(client: TestClient):
    """Test lấy thông tin người dùng hiện tại khi không có token."""
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_logout(authorized_client: TestClient):
    """Test đăng xuất."""
    response = authorized_client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Đăng xuất thành công"
    # Kiểm tra cookie đã được xóa
    assert "access_token" not in response.cookies


def test_refresh_token(authorized_client: TestClient):
    """Test làm mới token."""
    response = authorized_client.post("/auth/refresh")
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
