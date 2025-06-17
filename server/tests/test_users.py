"""
Tests cho các API endpoints trong users router.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user_model import User


def test_create_user(client: TestClient):
    """Test tạo người dùng mới."""
    user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "fullName": "New User",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["fullName"] == user_data["fullName"]
    assert "id" in data
    assert "hashedPassword" not in data


def test_create_user_existing_email(client: TestClient, test_user: User):
    """Test tạo người dùng với email đã tồn tại."""
    user_data = {
        "email": "test@example.com",  # Email đã tồn tại
        "password": "password123",
        "fullName": "Another User",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert "Email đã được đăng ký" in response.json()["detail"]


def test_get_users(superuser_client: TestClient):
    """Test lấy danh sách người dùng (yêu cầu quyền admin)."""
    response = superuser_client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Ít nhất có test_user và test_superuser


def test_get_users_unauthorized(authorized_client: TestClient):
    """Test lấy danh sách người dùng với người dùng thường."""
    response = authorized_client.get("/users/")
    assert response.status_code == 403
    assert "Không đủ quyền" in response.json()["detail"]


def test_get_user_by_id(superuser_client: TestClient, test_user: User):
    """Test lấy thông tin người dùng theo ID."""
    response = superuser_client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert "hashedPassword" not in data


def test_get_user_by_id_not_found(superuser_client: TestClient):
    """Test lấy thông tin người dùng với ID không tồn tại."""
    response = superuser_client.get("/users/999999")
    assert response.status_code == 404
    assert "Không tìm thấy người dùng" in response.json()["detail"]


def test_update_user(authorized_client: TestClient, test_user: User):
    """Test cập nhật thông tin người dùng."""
    update_data = {"fullName": "Updated Name"}
    response = authorized_client.patch(f"/users/{test_user.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["fullName"] == update_data["fullName"]
    assert data["email"] == test_user.email


def test_update_other_user(authorized_client: TestClient, test_superuser: User):
    """Test cập nhật thông tin người dùng khác (không phải admin)."""
    update_data = {"fullName": "Should Not Update"}
    response = authorized_client.patch(f"/users/{test_superuser.id}", json=update_data)
    assert response.status_code == 403
    assert "Không có quyền cập nhật người dùng khác" in response.json()["detail"]


def test_update_user_as_admin(superuser_client: TestClient, test_user: User):
    """Test cập nhật thông tin người dùng với quyền admin."""
    update_data = {"fullName": "Admin Updated", "isActive": False}
    response = superuser_client.patch(f"/users/{test_user.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["fullName"] == update_data["fullName"]
    assert data["isActive"] == update_data["isActive"]


def test_delete_user(superuser_client: TestClient, test_user: User):
    """Test xóa người dùng (yêu cầu quyền admin)."""
    response = superuser_client.delete(f"/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Người dùng đã được xóa thành công"

    # Kiểm tra người dùng đã bị xóa
    response = superuser_client.get(f"/users/{test_user.id}")
    assert response.status_code == 404


def test_delete_user_unauthorized(authorized_client: TestClient, test_superuser: User):
    """Test xóa người dùng không có quyền admin."""
    response = authorized_client.delete(f"/users/{test_superuser.id}")
    assert response.status_code == 403
    assert "Không đủ quyền" in response.json()["detail"]
