from typing import List

from bot.database.models import UserProfile
from bot.utils.functions import convert_number_to_emoji


def get_no_admins_found_message() -> str:
    return "📭 Nie znaleziono adminów.📭"


def get_log_no_admins_found_message() -> str:
    return "No admins found."


def get_log_admins_list_sent_message() -> str:
    return "Admin list sent to user."


def format_admins_list(admins: List[UserProfile]) -> str:
    admin_lines = []

    for idx, admin in enumerate(admins, start=1):
        line = f"{convert_number_to_emoji(idx)} | 🆔 {admin.user_id}\n   🧑‍💻 {admin.full_name or admin.username}\n   🗓 Subskrypcja do: {admin.subscription_end or 'N/A'}\n   📝 Note: {admin.note or 'Brak'}"
        admin_lines.append(line)

    response = "📃 Lista adminów:\n"
    response += "```\n" + "\n\n".join(admin_lines) + "\n```"
    return response
