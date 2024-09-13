from typing import List

from bot.database.models import UserProfile
from bot.utils.functions import format_user_list


def get_no_moderators_found_message() -> str:
    return "📭 Nie znaleziono moderatorów.📭"


def get_log_no_moderators_found_message() -> str:
    return "No moderators found."


def get_log_moderators_list_sent_message() -> str:
    return "Moderator list sent to user."


def format_moderators_list(moderators: List[UserProfile]) -> str:
    return format_user_list(moderators, "Lista moderatorów")
