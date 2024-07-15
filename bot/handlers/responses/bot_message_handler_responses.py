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
