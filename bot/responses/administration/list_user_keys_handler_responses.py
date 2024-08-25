from typing import List

from bot.database.models import UserMessage
from bot.utils.functions import convert_number_to_emoji


def create_user_keys_response(messages: List[UserMessage]) -> str:
    user_key_lines = []

    for idx, msg in enumerate(messages, start=1):
        line = f"{convert_number_to_emoji(idx)} | 🆔 {msg.user_id}\n   🔑 {msg.key or 'N/A'}\n   🕒 {msg.timestamp or 'N/A'}"
        user_key_lines.append(line)

    response = "📃 Lista kluczy użytkowników:\n"
    response += "```\n" + "\n\n".join(user_key_lines) + "\n```"
    return response


def get_user_keys_empty_message() -> str:
    return "📭 Brak zapisanych kluczy użytkowników.📭"


def get_log_user_keys_empty_message() -> str:
    return "User keys list is empty."


def get_log_user_keys_sent_message() -> str:
    return "User keys list sent to user."
