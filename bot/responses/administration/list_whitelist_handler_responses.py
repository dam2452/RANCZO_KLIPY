from typing import List

from bot.database.models import UserProfile
from bot.utils.functions import convert_number_to_emoji


def create_whitelist_response(users: List[UserProfile]) -> str:
    user_lines = []

    for idx, user in enumerate(users, start=1):
        line = (f"{convert_number_to_emoji(idx)} | 🆔 {user.user_id}\n   "
                f"🧑‍💻 {user.full_name or user.username}\n   🗓 Subskrypcja do: {user.subscription_end or 'N/A'}\n "
                f"  📝 Note: {user.note or 'Brak'}")
        user_lines.append(line)

    response = "📃 Lista użytkowników w Whitelist:\n"
    response += "```\n" + "\n\n".join(user_lines) + "\n```"
    return response


def get_whitelist_empty_message() -> str:
    return "📭 Whitelist jest pusta.📭"


def get_log_whitelist_empty_message() -> str:
    return "Whitelist is empty."


def get_log_whitelist_sent_message() -> str:
    return "Whitelist sent to user."
