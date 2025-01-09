import logging
from pathlib import Path
import re
from typing import (
    List,
    Optional,
)

from bot.database.database_manager import DatabaseManager
from bot.tests.settings import settings as s


def get_general_error_message() -> str:
    return "⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"


def get_invalid_args_count_message(action_name: str, user_id: int) -> str:
    return f"Incorrect command ({action_name}) format provided by user '{user_id}'."

def get_log_no_segments_found_message(quote: str) -> str:
    return f"No segments found for quote: '{quote}'"

def get_log_extraction_failure_message(exception: Exception) -> str:
    return f"Failed to extract video clip: {exception}"

def get_log_clip_duration_exceeded_message(user_id: int) -> str:
    return f"Clip duration limit exceeded for user '{user_id}'"

def get_clip_size_log_message(file_path: Path, file_size: float) -> str:
    return f"{file_path} Rozmiar klipu: {file_size:.2f} MB"


def get_clip_size_exceed_log_message(file_size: float, limit_size: float) -> str:
    return f"Rozmiar klipu {file_size:.2f} MB przekracza limit {limit_size} MB."

def get_video_sent_log_message(file_path: Path) -> str:
    return f"Wysłano plik wideo: {file_path}"

class MessageNotFoundError(Exception):
    pass

class MessageArgumentMismatchError(Exception):
    pass

class MessageFormattingError(Exception):
    pass

async def get_response(
    key: str,
    handler_name: str,
    args: Optional[List[str]] = None,
) -> str:
    message = await DatabaseManager.get_message_from_specialized_table(
        key, handler_name,
    )
    if not message:
        message = await DatabaseManager.get_message_from_common_messages(
            key, handler_name,
        )

    if not message:
        logging.debug(get_log_message_not_found(key, handler_name, s.SPECIALIZED_TABLE))
        raise MessageNotFoundError

    placeholder_count = len(re.findall(r"{}", message))
    args = args or []

    if len(args) != placeholder_count:
        logging.debug(get_log_argument_mismatch(key, handler_name, placeholder_count, len(args), message))
        raise MessageArgumentMismatchError

    try:
        final_message = message.format(*args)
    except IndexError as e:
        logging.debug(get_log_formatting_error(key, handler_name, message, args, e))
        raise MessageFormattingError(str(e)) from e

    return final_message

def get_log_message_not_found(key: str, handler_name: str, specialized_table: str) -> str:
    return (
        f"Message not found. key='{key}', handler_name='{handler_name}', "
        f"specialized_table='{specialized_table}'"
    )

def get_log_argument_mismatch(
    key: str, handler_name: str, expected_count: int, actual_count: int, message: str,
) -> str:
    return (
        f"Argument count mismatch for key='{key}', handler_name='{handler_name}'. "
        f"Expected {expected_count}, got {actual_count}. Message: {message}"
    )

def get_log_formatting_error(
    key: str, handler_name: str, message: str, args: List[str], error: Exception,
) -> str:
    return (
        f"Formatting error for key='{key}', handler_name='{handler_name}'. "
        f"Message: {message}, Args: {args}, Error: {error}"
    )
