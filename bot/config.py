import os
from dotenv import load_dotenv

# Ensure the .env file is in the same directory as this script
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)

# Get environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USERS_DB = os.getenv("USERS_DB", "db/users.db")
DEFAULT_ADMIN = os.getenv("DEFAULT_ADMIN")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if TELEGRAM_BOT_TOKEN is None:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in .env file")

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB]):
    raise ValueError("PostgreSQL connection parameters are not fully set in .env file")

