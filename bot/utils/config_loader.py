import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_env_file(env_file_var: str = 'ENV_FILE', default_env_name: str = ".env") -> Path:
    env_file = os.getenv(env_file_var)
    if env_file:
        env_path = Path(env_file)
    else:
        env_path = Path(__file__).parent.parent.parent / default_env_name
        print(env_path)

    if env_path.exists():
        load_dotenv(env_path)
        logger.warning(f"Using dotenv file: {env_path}")
    else:
        logger.info("No dotenv file found. Environment variables should be provided by the system.")
    return env_path
