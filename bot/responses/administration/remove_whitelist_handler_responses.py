def get_no_user_id_provided_message() -> str:
    return "⚠️ Nie podano ID użytkownika.⚠️"


def get_user_removed_message(username: str) -> str:
    return f"✅ Usunięto {username} z whitelisty.✅"


def get_log_user_removed_message(username: str, removed_by: str) -> str:
    return f"User {username} removed from whitelist by {removed_by}."
