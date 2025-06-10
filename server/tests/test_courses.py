"""
Tests cho các API endpoints trong courses router.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.course import Course


@pytest.fixture(scope="function")
def test_course(db: Session):
    """
    Fixture để tạo khóa học test trong database.
    """
    course_data = {
        "title": "Khóa học test",
        "description": "Mô tả khóa học test",
        "image_url": "https://example.com/image.jpg",
        "price": 100000,
        "is_published": True,
        "level": "Beginner",
    }

    course = Course(**course_data)
    db.add(course)
    db.commit()
    db.refresh(course)

    return course


def test_get_courses(client: TestClient, test_course: Course):
    """Test lấy danh sách khóa học."""
    response = client.get("/courses")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert "totalPages" in data
    assert len(data["items"]) >= 1
    assert data["total"] >= 1


def test_get_courses_pagination(client: TestClient, test_course: Course):
    """Test phân trang khi lấy danh sách khóa học."""
    # Tạo thêm 5 khóa học
    for i in range(5):
        client.post(
            "/courses",
            json={
                "title": f"Khóa học test {i}",
                "description": f"Mô tả khóa học test {i}",
                "imageUrl": "https://example.com/image.jpg",
                "price": 100000,
                "isPublished": True,
                "level": "Beginner",
            },
        )

    # Kiểm tra phân trang với limit=3
    response = client.get("/courses?page=1&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["limit"] == 3
    assert data["total"] >= 6  # 1 từ fixture + 5 mới tạo

    # Kiểm tra trang thứ 2
    response = client.get("/courses?page=2&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert data["page"] == 2


def test_get_course_by_id(client: TestClient, test_course: Course):
    """Test lấy thông tin chi tiết của một khóa học."""
    response = client.get(f"/courses/{test_course.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_course.id
    assert data["title"] == test_course.title
    assert data["description"] == test_course.description


def test_get_course_not_found(client: TestClient):
    """Test lấy thông tin khóa học không tồn tại."""
    response = client.get("/courses/999999")
    assert response.status_code == 404
    assert "Không tìm thấy khóa học" in response.json()["detail"]


def test_create_course(client: TestClient):
    """Test tạo khóa học mới."""
    course_data = {
        "title": "Khóa học mới",
        "description": "Mô tả khóa học mới",
        "imageUrl": "https://example.com/new-image.jpg",
        "price": 150000,
        "isPublished": True,
        "level": "Intermediate",
    }
    response = client.post("/courses", json=course_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == course_data["title"]
    assert data["description"] == course_data["description"]
    assert data["price"] == course_data["price"]
    assert "id" in data


def test_update_course(client: TestClient, test_course: Course):
    """Test cập nhật thông tin khóa học."""
    update_data = {"title": "Khóa học đã cập nhật", "price": 200000}
    response = client.put(f"/courses/{test_course.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["price"] == update_data["price"]
    assert data["description"] == test_course.description  # Không thay đổi


def test_update_course_not_found(client: TestClient):
    """Test cập nhật khóa học không tồn tại."""
    update_data = {"title": "Khóa học không tồn tại"}
    response = client.put("/courses/999999", json=update_data)
    assert response.status_code == 404
    assert "Không tìm thấy khóa học" in response.json()["detail"]


def test_delete_course(client: TestClient, test_course: Course):
    """Test xóa khóa học."""
    response = client.delete(f"/courses/{test_course.id}")
    assert response.status_code == 204

    # Kiểm tra khóa học đã bị xóa
    response = client.get(f"/courses/{test_course.id}")
    assert response.status_code == 404


def test_delete_course_not_found(client: TestClient):
    """Test xóa khóa học không tồn tại."""
    response = client.delete("/courses/999999")
    assert response.status_code == 404
    assert "Không tìm thấy khóa học" in response.json()["detail"]
