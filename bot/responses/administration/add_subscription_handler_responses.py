def get_subscription_log_message(username: str, executor: str) -> str:
    return f"Subscription for user {username} extended by {executor}."


def get_subscription_error_log_message() -> str:
    return "An error occurred while extending the subscription."
