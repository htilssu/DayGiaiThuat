from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# Tạo engine với các tùy chọn kết nối tối ưu
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,  # Kiểm tra kết nối trước khi sử dụng
    pool_size=5,  # Số lượng connection trong pool
    max_overflow=10,  # Số lượng connection có thể tạo thêm khi pool đầy
    pool_timeout=30,  # Thời gian chờ khi pool đầy
    pool_recycle=1800,  # Tái sử dụng connection sau 30 phút
)

# SessionLocal factory để tạo database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các model
Base = declarative_base()

# Dependency để lấy database session
def get_db():
    """
    Generator function để lấy database session và đảm bảo đóng session sau khi sử dụng
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 