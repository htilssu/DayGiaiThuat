"""
Fixtures cho pytest để sử dụng trong các test case.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_db
from app.models.user_model import User
from app.routers.router_router import register_router
from app.core.config import settings
from app.utils.oauth2.token import create_access_token

# Tạo database URL cho test
TEST_DB_USER = os.getenv("TEST_DB_USER", settings.DB_USER)
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", settings.DB_PASSWORD)
TEST_DB_HOST = os.getenv("TEST_DB_HOST", settings.DB_HOST)
TEST_DB_PORT = os.getenv("TEST_DB_PORT", settings.DB_PORT)
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_db")

# Connection string cho SQLAlchemy
TEST_DATABASE_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

# Tạo engine cho test database
engine = create_engine(TEST_DATABASE_URL)

# Tạo session factory cho test
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_test_db():
    """
    Fixture để thiết lập database cho test.
    Tạo tất cả các bảng trước khi chạy test và xóa sau khi test hoàn thành.
    """
    # Tạo database nếu chưa tồn tại
    temp_engine = create_engine(
        f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
    )
    with temp_engine.connect() as conn:
        conn.execute(text("COMMIT"))
        # Xóa database nếu đã tồn tại
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.execute(text("COMMIT"))
        # Tạo database mới
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    # Tạo tất cả các bảng trong database test
    Base.metadata.create_all(bind=engine)

    yield

    # Xóa tất cả các bảng sau khi test hoàn thành
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(setup_test_db) -> Generator:
    """
    Fixture để cung cấp database session cho mỗi test function.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Fixture để tạo TestClient cho FastAPI app.
    """
    # Tạo app test
    app = FastAPI()
    register_router(app)

    # Override dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_user(db) -> User:
    """
    Fixture để tạo user test trong database.
    """
    user_data = {
        "email": "test@example.com",
        "hashed_password": "$2b$12$1InH9LlUVpWA.cvbA9MrI.8CL1NW6vNrTZREV/ByPuXpBMWQnN3Uy",  # password: password123
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
    }

    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture(scope="function")
def test_superuser(db) -> User:
    """
    Fixture để tạo superuser test trong database.
    """
    user_data = {
        "email": "admin@example.com",
        "hashed_password": "$2b$12$1InH9LlUVpWA.cvbA9MrI.8CL1NW6vNrTZREV/ByPuXpBMWQnN3Uy",  # password: password123
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True,
    }

    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture(scope="function")
def token(test_user) -> str:
    """
    Fixture để tạo token cho test user.
    """
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture(scope="function")
def superuser_token(test_superuser) -> str:
    """
    Fixture để tạo token cho superuser.
    """
    return create_access_token(data={"sub": test_superuser.email})


@pytest.fixture(scope="function")
def authorized_client(client, token) -> TestClient:
    """
    Fixture để tạo TestClient với token authorization.
    """
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture(scope="function")
def superuser_client(client, superuser_token) -> TestClient:
    """
    Fixture để tạo TestClient với token authorization cho superuser.
    """
    client.headers = {**client.headers, "Authorization": f"Bearer {superuser_token}"}
    return client
