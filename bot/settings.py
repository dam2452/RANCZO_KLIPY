import os

from dotenv import load_dotenv
from pydantic import (
    Field,
    ValidationError,
)
from pydantic_settings import BaseSettings

# Ensure the .env file is loaded
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = Field(..., env='TELEGRAM_BOT_TOKEN')
    DEFAULT_ADMIN: str = Field(..., env='DEFAULT_ADMIN')

    POSTGRES_USER: str = Field(..., env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field(..., env='POSTGRES_PASSWORD')
    POSTGRES_HOST: str = Field(..., env='POSTGRES_HOST')
    POSTGRES_PORT: int = Field(..., env='POSTGRES_PORT')
    POSTGRES_DB: str = Field(..., env='POSTGRES_DB')

    ES_HOST: str = Field(..., env='ES_HOST')
    ES_USERNAME: str = Field(..., env='ES_USERNAME')
    ES_PASSWORD: str = Field(..., env='ES_PASSWORD')

    EXTEND_BEFORE: int = Field(5, env='EXTEND_BEFORE')
    EXTEND_AFTER: int = Field(5, env='EXTEND_AFTER')

    class Config:
        env_file = env_path


try:
    settings = Settings()
except ValidationError as e:
    raise ValueError(f"Configuration error: {e}") from e

# Access settings via the settings instance
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
DEFAULT_ADMIN = settings.DEFAULT_ADMIN

POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT
POSTGRES_DB = settings.POSTGRES_DB

EXTEND_BEFORE = settings.EXTEND_BEFORE
EXTEND_AFTER = settings.EXTEND_AFTER
