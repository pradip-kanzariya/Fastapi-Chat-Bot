from pydantic_settings import BaseSettings
import pytesseract
import os
import logging
from dotenv import load_dotenv
load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class ConfigurationSettings(BaseSettings):
    """All environment variables configuration and use through this class."""
    # Backend
    BACKEND_HOST : str = os.environ.get("BACKEND_HOST")
    BACKEND_PORT : int = os.environ.get("BACKEND_PORT")

    # Database
    DATABASE_URL : str = os.environ.get("DATABASE_URL")

    # Auth
    SECRET_KEY : str = os.environ.get("SECRET_KEY")
    ALGORITHM : str = os.environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES : int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")

    # Configure Tesseract
    tesseract_cmd : str = os.environ.get("TESSERACT_DIR")
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    # Configure Aws
    AWS_ACCESS_KEY_ID : str = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY : str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN : str = os.environ.get("AWS_SESSION_TOKEN")
    AWS_LLM_ID : str = os.environ.get("AWS_LLM_ID")
    AWS_ANTHROPIC_VERSION : str = os.environ.get("AWS_ANTHROPIC_VERSION")
    AWS_EMBEDDING_MODEL_ID : str = os.environ.get("AWS_EMBEDDING_MODEL_ID")
    AWS_REGION_NAME : str = os.environ.get("AWS_REGION_NAME")
    AWS_SERVICE_NAME : str = os.environ.get("AWS_SERVICE_NAME")

settings = ConfigurationSettings()