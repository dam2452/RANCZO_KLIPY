def get_log_no_report_content_message(username: str) -> str:
    return f"No report content provided by user '{username}'."


def get_log_report_received_message(username: str, report: str) -> str:
    return f"Report received from user '{username}': {report}"
