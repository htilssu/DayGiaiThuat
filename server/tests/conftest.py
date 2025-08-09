"""
Fixtures cho pytest để sử dụng trong các test case.
"""

import pytest
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database.database import get_async_db
from app.models.user_model import User
from app.utils.utils import create_access_token
from app.routers import router

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"

# Create async engine for tests
test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


def register_router(app):
    """
    Register all routers to the FastAPI app.
    """
    app.include_router(router)


@pytest.fixture(scope="session")
def setup_test_db():
    """
    Setup test database.
    """
    # Create tables
    from app.database.database import Base
    import asyncio
    
    async def create_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(create_tables())
    yield
    
    # Cleanup
    async def drop_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    asyncio.run(drop_tables())


@pytest.fixture(scope="function")
async def db(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture để tạo database session cho test.
    """
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Fixture để tạo TestClient cho FastAPI app.
    """
    # Tạo app test
    from fastapi import FastAPI
    app = FastAPI()
    register_router(app)

    # Override dependency
    async def override_get_async_db():
        yield db

    app.dependency_overrides[get_async_db] = override_get_async_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def test_user(db) -> User:
    """
    Fixture để tạo user test trong database.
    """
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "$2b$12$1InH9LlUVpWA.cvbA9MrI.8CL1NW6vNrTZREV/ByPuXpBMWQnN3Uy",  # password: password123
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False,
    }

    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@pytest.fixture(scope="function")
async def test_superuser(db) -> User:
    """
    Fixture để tạo superuser test trong database.
    """
    user_data = {
        "email": "admin@example.com",
        "username": "adminuser",
        "hashed_password": "$2b$12$1InH9LlUVpWA.cvbA9MrI.8CL1NW6vNrTZREV/ByPuXpBMWQnN3Uy",  # password: password123
        "full_name": "Admin User",
        "is_active": True,
        "is_admin": True,
    }

    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)

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
