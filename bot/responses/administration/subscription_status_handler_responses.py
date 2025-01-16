def get_log_subscription_status_sent_message(username: str) -> str:
    return f"Subscription status sent to user '{username}'."


def get_log_no_active_subscription_message(username: str) -> str:
    return f"No active subscription found for user '{username}'."
