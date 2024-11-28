import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# pylint: disable=duplicate-code
logger = logging.getLogger(__name__)

env_file = os.getenv('ENV_FILE')
if env_file:
    env_path = Path(env_file)
else:
    env_path = Path(__file__).parent.parent / ".env"

if env_path.exists():
    load_dotenv(env_path)
    logger.warning("Using dotenv file")
else:
    logger.info("No dotenv file found. Environment variables should be provided by the system.")
# pylint: enable=duplicate-code

class Settings(BaseSettings):

    SESSION: str = Field("name")
    API_ID: int = Field()
    API_HASH: str = Field()
    BOT_USERNAME: str = Field()
    PASSWORD: str = Field()
    PHONE: str = Field()

    TEST_POSTGRES_DB: str = Field()
    TEST_POSTGRES_USER: str = Field()
    TEST_POSTGRES_PASSWORD: str = Field()
    TEST_POSTGRES_HOST: str = Field()
    TEST_POSTGRES_PORT: str = Field()

    DEFAULT_ADMIN: int = Field(...)
    ADMIN_USERNAME: str = Field("Admin")
    ADMIN_FULL_NAME: str = Field("Admin")
    class Config:
        env_file = env_path
        env_prefix = ""
        extra = "ignore"

settings = Settings()
