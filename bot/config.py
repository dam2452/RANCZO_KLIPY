import os
from dotenv import load_dotenv

# Ensure the .env file is in the same directory as this script
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

if os.path.exists(env_path):
    print(f"Loading .env file from {env_path}")
    load_dotenv(env_path)
else:
    print(f".env file not found at {env_path}")

# Get environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WHITELIST_DB = os.getenv("WHITELIST_DB", "whitelist.db")
WHITELIST_PATH = os.getenv("WHITELIST_PATH", "./whitelist.txt")
ADMINS_PATH = os.getenv("ADMINS_PATH", "./admins.txt")

# Debugging prints
print("TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)
print("WHITELIST_DB:", WHITELIST_DB)
print("WHITELIST_PATH:", WHITELIST_PATH)
print("ADMINS_PATH:", ADMINS_PATH)

if TELEGRAM_BOT_TOKEN is None:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in .env file")
