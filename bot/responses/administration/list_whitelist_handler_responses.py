from typing import List
from bot.database.models import UserProfile
from tabulate import tabulate


def create_whitelist_response(users: List[UserProfile]) -> str:
    table = [["Username", "Full Name", "Email", "Phone", "Subskrypcja do"]]
    for user in users:
        table.append([
            user.username,
            user.full_name or "N/A",
            user.email or "N/A",
            user.phone or "N/A",
            user.subscription_end or "N/A"
        ])

    response = f"```whitelista\n{tabulate(table, headers='firstrow', tablefmt='grid')}```"
    return response


def get_whitelist_empty_message() -> str:
    return "📭 Whitelist jest pusta.📭"


def get_log_whitelist_empty_message() -> str:
    return "Whitelist is empty."


def get_log_whitelist_sent_message() -> str:
    return "Whitelist sent to user."
