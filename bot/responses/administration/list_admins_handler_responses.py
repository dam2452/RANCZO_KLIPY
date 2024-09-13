from typing import List

from bot.database.models import UserProfile
from bot.utils.functions import format_user_list


def get_no_admins_found_message() -> str:
    return "📭 Nie znaleziono adminów.📭"


def get_log_no_admins_found_message() -> str:
    return "No admins found."


def get_log_admins_list_sent_message() -> str:
    return "Admin list sent to user."


def format_admins_list(admins: List[UserProfile]) -> str:
    return format_user_list(admins, "Lista adminów")
