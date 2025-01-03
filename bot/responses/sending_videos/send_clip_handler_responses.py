from typing import Optional


def get_log_clip_not_found_message(clip_identifier: Optional[int], username: str) -> str:
    if clip_identifier is None:
        return f"No clip found by name for user: {username}"
    return f"No clip found with number {clip_identifier} for user: {username}"


def get_log_empty_clip_file_message(clip_name: str, username: str) -> str:
    return f"Clip file is empty for clip '{clip_name}' by user '{username}'."


def get_log_empty_file_error_message(clip_name: str, username: str) -> str:
    return f"File is empty after writing clip '{clip_name}' for user '{username}'."


def get_log_clip_sent_message(clip_name: str, username: str) -> str:
    return f"Clip '{clip_name}' sent to user '{username}' and temporary file removed."


