import logging

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Configuration settings for the application.
    """
    OPEN_AI_API_KEY: str = ""
    EMBEDDING_MODEL_NAME: str = "text-embedding-004"
    GEMINI_AI_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Config()
logger = logging.getLogger()
logger.info("Configuration loaded successfully.")
