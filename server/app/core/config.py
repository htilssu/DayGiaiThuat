import json
from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Cấu hình ứng dụng, đọc từ biến môi trường

    Attributes:
        PROJECT_NAME (str): Tên dự án
        DEV_MODE (bool): Mode phát triển
        BACKEND_CORS_ORIGINS (List[AnyHttpUrl]): Danh sách origins được phép CORS
        DB_USER (str): Username database
        DB_PASSWORD (str): Password database
        DB_HOST (str): Host database
        DB_PORT (str): Port database
        DB_NAME (str): Tên database
        SECRET_KEY (str): Key để mã hóa JWT token
        AGENT_LLM_MODEL (str): Model LLM cho agent
        CREATIVE_LLM_MODEL (str): Model LLM cho creative
        EMBEDDING_MODEL (str): Model embedding
        PINECONE_API_KEY (str): API key cho Pinecone
        MONGO_URI (str): URI cho MongoDB
        LANGSMITH_API_KEY (str): API key cho LangSmith
        LANGSMITH_TRACING (bool): Tracing cho LangSmith
        LANGSMITH_PROJECT (str): Project cho LangSmith
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Thời gian hết hạn của token (phút)
        COOKIE_DOMAIN (str): Domain cho cookie
        COOKIE_SECURE (bool): Secure flag cho cookie
        COOKIE_SAMESITE (str): SameSite setting cho cookie
        COOKIE_NAME (str): Tên cookie lưu JWT token
        RUN_MIGRATIONS_ON_STARTUP (bool): Chạy migration khi khởi động
        RUN_SEEDERS_ON_STARTUP (bool): Chạy seeder khi khởi động
        SEEDERS_TO_RUN (List[str]): Danh sách các seeder cần chạy
        FORCE_SEEDERS (bool): Xóa dữ liệu cũ trước khi tạo mới
        S3_ACCESS_KEY_ID (str): S3 Access Key ID
        S3_SECRET_ACCESS_KEY (str): S3 Secret Access Key
        S3_REGION (str): S3 Region
        S3_BUCKET_NAME (str): Tên bucket S3
        S3_COURSE_IMAGE_PREFIX (str): Prefix cho ảnh khóa học trong S3
        S3_USER_AVATAR_PREFIX (str): Prefix cho avatar người dùng trong S3
        S3_PUBLIC_URL (str): URL công khai cho bucket S3
        S3_ENDPOINT_URL (str): URL endpoint cho Cloudflare R2
        UVICORN_WORKERS (int): Số workers cho uvicorn
        UVICORN_HOST (str): Host cho uvicorn
        UVICORN_PORT (int): Port cho uvicorn
        UVICORN_RELOAD (bool): Auto reload cho uvicorn
    """

    PROJECT_NAME: str = "default"
    DEV_MODE: Optional[bool] = True
    # CORS
    BACKEND_CORS_ORIGINS: List[str]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
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
                # Thử parse JSON string
                return json.loads(v)
            except json.JSONDecodeError:
                # Nếu không phải JSON, split theo dấu phẩy
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

    # File Upload Settings
    UPLOAD_DIR: str = "uploads"  # Thư mục lưu file tạm thời

    # Document Processing Settings
    DOCUMENT_PROCESSING_ENDPOINT: Optional[str] = (
        None  # External API endpoint for document processing
    )
    DOCUMENT_PROCESSING_TIMEOUT: int = 300  # Timeout cho API call (seconds)
    S3_DOCUMENT_PREFIX: str = "documents/"  # Prefix cho documents trong S3
    BASE_URL: str = "http://localhost:8000"  # Base URL for webhook callbacks

    # AWS/S3 Boto3 Settings (fix for MissingContentLength error)
    AWS_REQUEST_CHECKSUM_CALCULATION: str = "when_required"
    AWS_RESPONSE_CHECKSUM_VALIDATION: str = "when_required"

    # AWS S3 Settings / Cloudflare R2 Settings
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

    # Migration và Seeder
    RUN_MIGRATIONS_ON_STARTUP: bool = False
    RUN_SEEDERS_ON_STARTUP: bool = False
    SEEDERS_TO_RUN: Optional[List[str]] = None
    FORCE_SEEDERS: bool = False

    # Judge0
    JUDGE0_API_URL: str

    # RunPod API
    RUNPOD_API_KEY: Optional[str] = None

    # Storage Service Settings
    STORAGE_RETRY_ATTEMPTS: int = 3
    
    # RunPod Settings
    RUNPOD_ENDPOINT_ID: Optional[str] = None  # RunPod endpoint ID for document processing

    @field_validator("SEEDERS_TO_RUN", mode="before")
    def assemble_seeders_to_run(
        cls, v: Optional[Union[str, List[str]]]
    ) -> Optional[List[str]]:
        """
        Xử lý giá trị SEEDERS_TO_RUN từ biến môi trường

        Args:
            v (Optional[Union[str, List[str]]]): Giá trị từ biến môi trường

        Returns:
            Optional[List[str]]: Danh sách các seeder cần chạy
        """
        if v is None:
            return None

        if isinstance(v, str):
            try:
                # Thử parse JSON string
                return json.loads(v)
            except json.JSONDecodeError:
                # Nếu không phải JSON, split theo dấu phẩy
                return [i.strip() for i in v.split(",")]
        return v

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
            self.S3_ACCESS_KEY_ID and self.S3_SECRET_ACCESS_KEY and self.S3_BUCKET_NAME and self.S3_REGION
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


# Tạo instance của Settings để sử dụng trong ứng dụng
settings = Settings()
