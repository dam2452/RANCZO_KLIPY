def get_clip_not_found_message(clip_name: str) -> str:
    return f"❌ Nie znaleziono klipu o nazwie '{clip_name}'.❌"


def get_empty_clip_file_message() -> str:
    return "⚠️ Plik klipu jest pusty.⚠️"


def get_empty_file_error_message() -> str:
    return "⚠️ Wystąpił błąd podczas wysyłania klipu. Plik jest pusty.⚠️"


def get_log_clip_not_found_message(clip_name: str, username: str) -> str:
    return f"Clip '{clip_name}' not found for user '{username}'."


def get_log_empty_clip_file_message(clip_name: str, username: str) -> str:
    return f"Clip file is empty for clip '{clip_name}' by user '{username}'."


def get_log_empty_file_error_message(clip_name: str, username: str) -> str:
    return f"File is empty after writing clip '{clip_name}' for user '{username}'."


def get_log_clip_sent_message(clip_name: str, username: str) -> str:
    return f"Clip '{clip_name}' sent to user '{username}' and temporary file removed."
