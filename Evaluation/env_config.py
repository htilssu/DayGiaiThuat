import logging

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Configuration settings for the application.
    """
    AI_API_KEY: str = ""
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"


settings = Config()
logger = logging.getLogger()
logger.info("Configuration loaded successfully.")
