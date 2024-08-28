import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

env_path: str = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)


class Settings(BaseSettings):
    TELEGRAM_FILE_SIZE_LIMIT_MB: int = Field(50)

    TELEGRAM_BOT_TOKEN: str = Field(...)
    DEFAULT_ADMIN: str = Field(...)

    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: int = Field(...)
    POSTGRES_DB: str = Field(...)

    ES_HOST: str = Field(...)
    ES_USER: str = Field(...)
    ES_PASS: str = Field(...)

    EXTEND_BEFORE: float = Field(5)
    EXTEND_AFTER: float = Field(5)

    EXTEND_BEFORE_COMPILE: float = Field(1)
    EXTEND_AFTER_COMPILE: float = Field(1)

    MESSAGE_LIMIT: int = Field(5)
    LIMIT_DURATION: int = Field(30)
    MAX_CLIPS_PER_COMPILATION: int = Field(30)
    MAX_ADJUSTMENT_DURATION: int = Field(20)
    MAX_SEARCH_QUERY_LENGTH: int = Field(200)
    MAX_CLIP_DURATION: int = Field(60)
    MAX_CLIP_NAME_LENGTH: int = Field(40)
    MAX_REPORT_LENGTH: int = Field(1000)

    class Config:
        env_file = env_path
        env_prefix = ""


settings = Settings()
