def get_no_message_provided_message() -> str:
    return "⚠️ Nie podano wiadomości.⚠️"


def get_message_saved_confirmation() -> str:
    return "✅Twoja wiadomość została zapisana.✅"


def get_log_message_saved(user_id: int) -> str:
    return f"Message from user {user_id} saved."
