import json
from typing import List, Optional

from pydantic import validator, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Cấu hình ứng dụng, đọc từ biến môi trường
    
    Attributes:
        PROJECT_NAME (str): Tên dự án
        BACKEND_CORS_ORIGINS (List[AnyHttpUrl]): Danh sách origins được phép CORS
        DB_USER (str): Username database
        DB_PASSWORD (str): Password database
        DB_HOST (str): Host database
        DB_PORT (str): Port database
        DB_NAME (str): Tên database
        SECRET_KEY (str): Key để mã hóa JWT token
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Thời gian hết hạn của token (phút)
        COOKIE_DOMAIN (str): Domain cho cookie
        COOKIE_SECURE (bool): Secure flag cho cookie
        COOKIE_SAMESITE (str): SameSite setting cho cookie
        COOKIE_NAME (str): Tên cookie lưu JWT token
    """
    PROJECT_NAME: str

    # CORS
    BACKEND_CORS_ORIGINS: List[str]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
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
    COOKIE_SECURE: bool = False  # True trong production
    COOKIE_SAMESITE: str = "lax"  # 'lax', 'strict', or 'none'
    COOKIE_NAME: str = "access_token"
    COOKIE_HTTPONLY: bool = True
    COOKIE_MAX_AGE: int = 3600  # phút, tương đương với ACCESS_TOKEN_EXPIRE_MINUTES

    # Agent
    GOOGLE_API_KEY: str
    PINECONE_API_KEY: str
    MONGO_URI: str
    LANGSMITH_API_KEY: str
    LANGSMITH_TRACING: bool = False
    LANGSMITH_PROJECT: str = "default"

    @property
    def DATABASE_URI(self) -> str:
        """
        Tạo connection string cho database
        
        Returns:
            str: Connection string
        """
        # Sử dụng driver psycopg2 thay vì asyncpg cho SQLAlchemy đồng bộ
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True
        env_file = ".env"


# Tạo instance của Settings để sử dụng trong ứng dụng
settings = Settings()
