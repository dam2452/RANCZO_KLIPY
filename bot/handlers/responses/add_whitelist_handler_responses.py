

def get_no_username_provided_message() -> str:
    return "✏️ Podaj nazwę użytkownika.✏️"


def get_user_added_message(username: str) -> str:
    return f"✅ Dodano {username} do whitelisty.✅"


def get_log_user_added_message(username: str, executor: str) -> str:
    return f"User {username} added to whitelist by {executor}."
