import logging
from streamlit_cookies_manager import EncryptedCookieManager
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Centralized configuration for cookies
cookies = EncryptedCookieManager(
    prefix=os.environ.get("COOKIES_PREFIX"),
    password=os.environ.get("COOKIES_SECRET"),
)

class ConfigurationSettings(BaseSettings):
    """All .env variable configuration in Settings."""
    BACKEND_HOST : str = os.environ.get("BACKEND_HOST")
    BACKEND_PORT : int = os.environ.get("BACKEND_PORT")

settings = ConfigurationSettings()
