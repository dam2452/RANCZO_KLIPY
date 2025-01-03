def get_log_user_removed_message(username: str, removed_by: str) -> str:
    return f"User {username} removed from whitelist by {removed_by}."

def get_log_user_not_in_whitelist_message(user_id: int) -> str:
    return f"User {user_id} not found in whitelist."
