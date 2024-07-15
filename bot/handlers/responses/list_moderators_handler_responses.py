from typing import List
import asyncpg


def get_no_moderators_found_message() -> str:
    return "📭 Nie znaleziono moderatorów.📭"


def format_user(user: asyncpg.Record) -> str:
    return (
        f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 "
        f"Phone: {user['phone']}"
    )


def get_users_string(users: List[asyncpg.Record]) -> str:
    return "\n".join([format_user(user) for user in users]) + "\n"


def get_log_no_moderators_found_message() -> str:
    return "No moderators found."


def get_log_moderators_list_sent_message() -> str:
    return "Moderator list sent to user."
