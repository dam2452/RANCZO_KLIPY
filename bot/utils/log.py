import logging
from typing import Dict

from bot.database.database_manager import DatabaseManager

LOG_LEVELS: Dict[int, str] = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
}


async def log_system_message(level: int, message: str, logger: logging.Logger) -> None:
    logger.log(level, message)
    await DatabaseManager.log_system_message(LOG_LEVELS[level], message)


async def log_user_activity(user_id: int, message: str, logger: logging.Logger) -> None:
    await log_system_message(logging.INFO, message, logger)
    await DatabaseManager.log_user_activity(user_id, message)
