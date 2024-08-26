def get_invalid_args_count_message() -> str:
    return "❌ Podaj nazwę klipu do usunięcia. Przykład: /usunklip nazwa_klipu ❌"


def get_clip_not_exist_message(clip_name: str) -> str:
    return f"🚫 Klip o nazwie '{clip_name}' nie istnieje.🚫"


def get_clip_deleted_message(clip_name: str) -> str:
    return f"✅ Klip o nazwie '{clip_name}' został usunięty.✅"


def get_log_clip_not_exist_message(clip_name: str, username: str) -> str:
    return f"Clip '{clip_name}' does not exist for user '{username}'."


def get_log_clip_deleted_message(clip_name: str, username: str) -> str:
    return f"Clip '{clip_name}' has been successfully deleted for user '{username}'."


def get_clip_name_length_exceeded_message():
    return "❌ Przekroczono limit długości nazwy klipu.❌"
