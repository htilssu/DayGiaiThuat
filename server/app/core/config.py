import json
from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "default"
    DEV_MODE: Optional[bool] = True
    # CORS
    BACKEND_CORS_ORIGINS: List[str]

    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """
        Xử lý giá trị BACKEND_CORS_ORIGINS từ biến môi trường

        Args:
            v (Union[str, List[str]]): Giá trị từ biến môi trường

        Returns:
            List[str]: Danh sách các origin được phép

        Raises:
            ValueError: Nếu giá trị không hợp lệ
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.split(",")]
        return v

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Cookie settings
    COOKIE_DOMAIN: Optional[str] = ""  # Sử dụng chuỗi rỗng thay vì None
    COOKIE_SECURE: bool = True  # True trong production
    COOKIE_SAMESITE: str = "lax"  # 'lax', 'strict', or 'none'
    COOKIE_NAME: str = "access_token"
    COOKIE_HTTPONLY: bool = True
    COOKIE_MAX_AGE: int = 60 * 60 * 30 * 24  # 30 ngày

    # Agent
    GOOGLE_API_KEY: str
    AGENT_LLM_MODEL: str
    CREATIVE_LLM_MODEL: str
    EMBEDDING_MODEL: str
    PINECONE_API_KEY: str
    MONGO_URI: str
    LANGSMITH_API_KEY: str
    LANGSMITH_TRACING: bool = False
    LANGSMITH_PROJECT: str = "default"

    UPLOAD_DIR: str = "uploads"  # Thư mục lưu file tạm thời

    DOCUMENT_PROCESSING_ENDPOINT: Optional[str] = None
    RUNPOD_API_KEY: str
    DOCUMENT_PROCESSING_TIMEOUT: int = 300
    S3_DOCUMENT_PREFIX: str = "documents/"
    BASE_URL: str = "http://localhost:8000"

    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_REGION: Optional[str] = (
        None  # Cho Cloudflare R2, có thể là "auto" hoặc region cụ thể
    )
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = (
        None  # Cho Cloudflare R2: https://[account-id].r2.cloudflarestorage.com
    )
    S3_COURSE_IMAGE_PREFIX: str = "course-images/"
    S3_USER_AVATAR_PREFIX: str = "user-avatars/"
    S3_PUBLIC_URL: Optional[str] = None  # CloudFront URL hoặc S3 public URL

    JUDGE0_API_URL: str

    @property
    def DATABASE_URI(self) -> str:
        """
        Tạo connection string đồng bộ cho database sử dụng psycopg2

        Returns:
            str: Sync connection string
        """
        # Sử dụng driver psycopg2 cho SQLAlchemy đồng bộ
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ASYNC_DATABASE_URI(self) -> str:
        """
        Tạo connection string bất đồng bộ cho database sử dụng asyncpg

        Returns:
            str: Async connection string
        """
        # Sử dụng driver asyncpg cho SQLAlchemy bất đồng bộ
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def S3_ENABLED(self) -> bool:
        """
        Kiểm tra xem S3/R2 đã được cấu hình đúng chưa

        Returns:
            bool: True nếu S3/R2 đã được cấu hình đầy đủ
        """
        return bool(
            self.S3_ACCESS_KEY_ID
            and self.S3_SECRET_ACCESS_KEY
            and self.S3_BUCKET_NAME
            and self.S3_REGION
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


# Tạo instance của Settings để sử dụng trong ứng dụng
settings = Settings()
