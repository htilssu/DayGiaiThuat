from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

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