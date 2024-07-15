from typing import List

import asyncpg


def get_general_error_message() -> str:
    return "⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"


def get_invalid_args_count_message(action_name: str) -> str:
    return f"Incorrect command ({action_name}) format provided by user."


def format_user(user: asyncpg.Record) -> str:
    return (
        f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 "
        f"Phone: {user['phone']}"
    )


def get_users_string(users: List[asyncpg.Record]) -> str:
    return "\n".join([format_user(user) for user in users]) + "\n"


def get_no_segments_found_message(quote: str) -> str:
    return f"❌ Nie znaleziono pasujących cytatów dla: '{quote}'.❌"


def get_log_no_segments_found_message(quote: str) -> str:
    return f"No segments found for quote: '{quote}'"


def get_extraction_failure_message() -> str:
    return "⚠️ Nie udało się wyodrębnić klipu wideo.⚠️"


def get_log_extraction_failure_message(exception: Exception) -> str:
    return f"Failed to extract video clip: {exception}"
