from typing import List

from bot.database.models import UserProfile
from bot.utils.functions import convert_number_to_emoji


def get_no_moderators_found_message() -> str:
    return "📭 Nie znaleziono moderatorów.📭"


def get_log_no_moderators_found_message() -> str:
    return "No moderators found."


def get_log_moderators_list_sent_message() -> str:
    return "Moderator list sent to user."


def format_moderators_list(moderators: List[UserProfile]) -> str:
    moderator_lines = []

    for idx, moderator in enumerate(moderators, start=1):
        line = f"{convert_number_to_emoji(idx)} | 🆔 ID: {moderator.user_id}\n   🧑‍💻 {moderator.full_name or moderator.username}\n   🗓 Subskrypcja do: {moderator.subscription_end or 'N/A'}\n   📝 Note: {moderator.note or 'Brak'}"
        moderator_lines.append(line)

    response = "📃 Lista moderatorów:\n"
    response += "```\n" + "\n\n".join(moderator_lines) + "\n```"
    return response
