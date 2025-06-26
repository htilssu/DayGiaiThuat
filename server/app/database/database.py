from datetime import datetime

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# Tạo engine để kết nối database với timeout ngắn hơn để tránh treo ứng dụng nếu không kết nối được
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,  # Kiểm tra kết nối trước khi sử dụng
    connect_args={"connect_timeout": 5},  # Timeout 5 giây
)

# Tạo engine bất đồng bộ
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    pool_pre_ping=True,  # Kiểm tra kết nối trước khi sử dụng
    connect_args={"connect_timeout": 5},  # Timeout 5 giây
)

# Tạo SessionLocal class để tạo session cho mỗi request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo AsyncSessionLocal class để tạo session bất đồng bộ
AsyncSessionLocal = async_sessionmaker(
    async_engine, autocommit=False, autoflush=False, expire_on_commit=False
)


# Tạo Base class để kế thừa cho các model
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )


def get_db():
    """
    Tạo và trả về một database session mới cho mỗi request
    và đảm bảo đóng kết nối sau khi xử lý xong.

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_session() -> AsyncSession:
    """
    Tạo và trả về một database session bất đồng bộ mới cho mỗi request
    và đảm bảo đóng kết nối sau khi xử lý xong.

    Yields:
        AsyncSession: Async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
