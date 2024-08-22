from typing import List

from tabulate import tabulate

from bot.database.models import UserMessage


def create_user_messages_response(messages: List[UserMessage]) -> str:
    table = [["User ID", "Message Content", "Timestamp"]]
    for msg in messages:
        table.append([
            msg.user_id,
            msg.message_content or "N/A",
            msg.timestamp or "N/A",
        ])

    response = f"```user_messages\n{tabulate(table, headers='firstrow', tablefmt='grid')}```"
    return response


def get_user_messages_empty_message() -> str:
    return "📭 Brak zapisanych wiadomości użytkowników.📭"


def get_log_user_messages_empty_message() -> str:
    return "User messages list is empty."


def get_log_user_messages_sent_message() -> str:
    return "User messages list sent to user."
