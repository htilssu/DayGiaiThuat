from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import json

class Settings(BaseSettings):
    """
    Cấu hình ứng dụng, đọc từ biến môi trường
    
    Attributes:
        API_V1_STR (str): Prefix cho API v1
        PROJECT_NAME (str): Tên dự án
        BACKEND_CORS_ORIGINS (List[AnyHttpUrl]): Danh sách origins được phép CORS
        DB_USER (str): Username database
        DB_PASSWORD (str): Password database
        DB_HOST (str): Host database
        DB_PORT (str): Port database
        DB_NAME (str): Tên database
        SECRET_KEY (str): Key để mã hóa JWT token
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Thời gian hết hạn của token (phút)
    """
    API_V1_STR: str
    PROJECT_NAME: str
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def DATABASE_URI(self) -> str:
        """
        Tạo connection string cho database
        
        Returns:
            str: Connection string
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True
        env_file = ".env"

# Tạo instance của Settings để sử dụng trong ứng dụng
settings = Settings() 