from pathlib import Path
import re
from typing import (
    List,
    Optional,
)

from bot.database.database_manager import DatabaseManager
from bot.settings import settings as s


class CustomError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class MessageNotFoundError(CustomError):
    def __init__(self, key: str, handler_name: str, specialized_table: str):
        message = (
            f"Message not found. key='{key}', handler_name='{handler_name}', "
            f"specialized_table='{specialized_table}'"
        )
        super().__init__(message)


class MessageArgumentMismatchError(CustomError):
    def __init__(self, key: str, handler_name: str, expected_count: int, actual_count: int, message_template: str):
        message = (
            f"Argument count mismatch for key='{key}', handler_name='{handler_name}'. "
            f"Expected {expected_count}, got {actual_count}. Template: {message_template}"
        )
        super().__init__(message)


class MessageFormattingError(CustomError):
    def __init__(self, key: str, handler_name: str, message_template: str, args: List[str], error: Exception):
        formatted_args = ', '.join(args) if args else "None"
        message = (
            f"Formatting error for key='{key}', handler_name='{handler_name}'. "
            f"Template: {message_template}, Args: [{formatted_args}], Error: {error}"
        )
        super().__init__(message)


async def get_response(
    key: str,
    handler_name: str,
    args: Optional[List[str]] = None,
) -> str:
    message = await DatabaseManager.get_message_from_specialized_table(key, handler_name)
    if not message:
        message = await DatabaseManager.get_message_from_common_messages(key, handler_name)

    if not message:
        raise MessageNotFoundError(key, handler_name, s.SPECIALIZED_TABLE)

    placeholder_count = len(re.findall(r"{}", message))
    args = args or []

    if len(args) != placeholder_count:
        raise MessageArgumentMismatchError(key, handler_name, placeholder_count, len(args), message)

    try:
        return message.format(*args)
    except IndexError as e:
        raise MessageFormattingError(key, handler_name, message, args, e) from e


def get_general_error_message() -> str:
    return "⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"


def get_invalid_args_count_message(action_name: str, user_id: int) -> str:
    return f"Incorrect command ({action_name}) format provided by user '{user_id}'."


def get_log_no_segments_found_message(quote: str) -> str:
    return f"No segments found for quote: '{quote}'"


def get_log_extraction_failure_message(exception: Exception) -> str:
    return f"Failed to extract video clip: {exception}"


def get_log_clip_duration_exceeded_message(user_id: int) -> str:
    return f"Clip duration limit exceeded for user '{user_id}'."


def get_clip_size_log_message(file_path: Path, file_size: float) -> str:
    return f"{file_path} Clip size: {file_size:.2f} MB."


def get_clip_size_exceed_log_message(file_size: float, limit_size: float) -> str:
    return f"Clip size {file_size:.2f} MB exceeds the limit of {limit_size} MB."


def get_video_sent_log_message(file_path: Path) -> str:
    return f"Video file sent: {file_path}"
