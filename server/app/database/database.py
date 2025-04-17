from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from alembic.config import Config
from alembic import command
import contextlib
import io

from app.core.config import settings

# Tạo logger
logger = logging.getLogger(__name__)

# Tạo engine để kết nối database với timeout ngắn hơn để tránh treo ứng dụng nếu không kết nối được
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,  # Kiểm tra kết nối trước khi sử dụng
    connect_args={"connect_timeout": 5}  # Timeout 5 giây
)

# Tạo SessionLocal class để tạo session cho mỗi request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo Base class để kế thừa cho các model
Base = declarative_base()

def run_migrations():
    """
    Chạy migration tự động khi ứng dụng khởi động sử dụng Alembic API
    
    Returns:
        bool: True nếu migration thành công, False nếu có lỗi
    """
    try:
        logger.info("Bắt đầu chạy migrations...")
        
        alembic_cfg = Config("alembic.ini")
        
        # Đặt URL kết nối database
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URI)
        
        # Chạy migration để cập nhật schema lên phiên bản mới nhất
        with engine.connect() as connection:
            alembic_cfg.attributes["connection"] = connection
            command.upgrade(alembic_cfg, "head")
        
        
        logger.info("Migration hoàn tất thành công!")
        return True
    except Exception as e:
        logger.error(f"Lỗi trong quá trình migration: {str(e)}")
        return False