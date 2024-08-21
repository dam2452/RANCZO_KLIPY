from typing import List

from tabulate import tabulate

from bot.database.models import UserProfile


def create_whitelist_response(users: List[UserProfile]) -> str:
    table = [["Username", "Full Name", "Subskrypcja do", "Note"]]
    for user in users:
        table.append([
            user.username or "N/A",
            user.full_name or "N/A",
            user.subscription_end or "N/A",
            user.note or "N/A",
        ])

    response = f"```whitelista\n{tabulate(table, headers='firstrow', tablefmt='grid')}```"
    return response


def get_whitelist_empty_message() -> str:
    return "📭 Whitelist jest pusta.📭"


def get_log_whitelist_empty_message() -> str:
    return "Whitelist is empty."


def get_log_whitelist_sent_message() -> str:
    return "Whitelist sent to user."
