def get_log_clip_not_exist_message(clip_number: int, username: str) -> str:
    return f"Clip '{clip_number}' does not exist for user '{username}'."


def get_log_clip_deleted_message(clip_name: str, username: str) -> str:
    return f"Clip '{clip_name}' has been successfully deleted for user '{username}'."
