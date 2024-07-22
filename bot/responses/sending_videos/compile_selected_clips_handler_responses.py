def get_invalid_args_count_message() -> str:
    return "📄 Podaj nazwy klipów do skompilowania w odpowiedniej kolejności."


def get_no_matching_clips_found_message() -> str:
    return "❌ Nie znaleziono pasujących klipów do kompilacji."


def get_clip_not_found_message(clip_name: str) -> str:
    return f"❌ Nie znaleziono klipu o nazwie '{clip_name}'."


def get_log_no_matching_clips_found_message() -> str:
    return "No matching clips found for compilation."


def get_log_clip_not_found_message(clip_name: str, username: str) -> str:
    return f"Clip '{clip_name}' not found for user '{username}'."


def get_compiled_clip_sent_message(username: str) -> str:
    return f"Compiled clip sent to user '{username}' and temporary files removed."
