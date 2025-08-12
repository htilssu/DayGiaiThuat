from datetime import datetime
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import DateTime, func, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# Tạo engine bất đồng bộ với cấu hình tối ưu
# asyncpg không hỗ trợ connect_timeout, sử dụng server_settings
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    pool_pre_ping=True,  # Kiểm tra kết nối trước khi sử dụng
    connect_args={
        "server_settings": {
            "application_name": "ai_agent_giai_thuat",
        },
        "command_timeout": 5,  # Timeout cho asyncpg commands
    },
    pool_timeout=30,  # Timeout để lấy connection từ pool
    pool_recycle=3600,  # Recycle connections mỗi giờ
)

# Tạo AsyncSessionLocal class với tối ưu hóa
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

"""
Synchronous SQLAlchemy engine and Session for scripting utilities

Note: The application uses async sessions by default. The following sync engine
and session factory are provided to support utility scripts like database
seeders that run outside the ASGI context.
"""

# Sync engine (psycopg2)
sync_engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Sync Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


# Tạo Base class để kế thừa cho các model
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )


async def get_async_db():
    """
    Tạo và trả về một database session bất đồng bộ mới cho mỗi request
    và đảm bảo đóng kết nối sau khi xử lý xong.

    Yields:
        AsyncSession: Async database session
    """
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_independent_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Tạo một session DB độc lập, không phụ thuộc vào request,
    dành cho các background task.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def check_async_db_connection() -> bool:
    """
    Kiểm tra kết nối database bất đồng bộ

    Returns:
        bool: True nếu kết nối thành công
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(func.now())
            result.fetchone()
        return True
    except Exception as e:
        print(f"Database async connection error: {e}")
        return False


def get_db():
    """
    Legacy sync database dependency - DEPRECATED
    Use get_async_db() instead for all new code
    """
    raise NotImplementedError(
        "Synchronous database access is deprecated. Use get_async_db() instead."
    )
