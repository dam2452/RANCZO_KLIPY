def get_log_start_message_sent(username: str) -> str:
    return f"Start message sent to user '{username}'"


def get_log_received_start_command(username: str, content: str) -> str:
    return f"Received start command from user '{username}' with content: {content}"
