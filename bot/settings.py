import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Ensure the .env file is loaded
env_path: str = os.path.join(os.path.dirname(__file__), '..', '.env')
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
