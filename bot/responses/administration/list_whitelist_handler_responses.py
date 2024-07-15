from typing import List

import asyncpg
from tabulate import tabulate


def create_whitelist_response(users: List[asyncpg.Record]) -> str:
    table = [["Username", "Full Name", "Email", "Phone", "Subskrypcja do"]]
    for user in users:
        table.append([user['username'], user['full_name'], user['email'], user['phone'], user['subscription_end']])

    response = f"```whitelista\n{tabulate(table, headers='firstrow', tablefmt='grid')}```"
    return response


def get_whitelist_empty_message() -> str:
    return "📭 Whitelist jest pusta.📭"


def get_log_whitelist_empty_message() -> str:
    return "Whitelist is empty."


def get_log_whitelist_sent_message() -> str:
    return "Whitelist sent to user."
