from pydantic_settings import BaseSettings
import pytesseract
from typing import List
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class ConfigurationSettings(BaseSettings):
    """All environment variables configuration and use through this class."""

    # Backend
    BACKEND_HOST: str
    BACKEND_PORT: int

    # Database
    DATABASE_URL: str

    # Auth
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Configure Tesseract
    TESSERACT_DIR: str

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SESSION_TOKEN: str
    AWS_LLM_ID: str
    AWS_ANTHROPIC_VERSION: str
    AWS_EMBEDDING_MODEL_ID: str
    AWS_REGION_NAME: str
    AWS_SERVICE_NAME: str

    # Cookies
    COOKIES_PREFIX: str
    COOKIES_SECRET: str

    # Middlewares
    ALLOW_ORIGINS: List[str] = ["*"]
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    class Config:
        env_file = ".env"   # automatically loads from .env
        extra = "allow"     # ignore unknown .env keys


settings = ConfigurationSettings()

# configure tesseract at runtime
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_DIR