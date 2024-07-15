def get_no_username_provided_message() -> str:
    return "✏️ Podaj nazwę użytkownika.✏️"


def get_user_updated_message(username: str) -> str:
    return f"✅ Zaktualizowano dane użytkownika {username}.✅"


def get_log_user_updated_message(username: str, updater: str) -> str:
    return f"User {username} updated by {updater}."
