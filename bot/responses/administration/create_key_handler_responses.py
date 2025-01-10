def get_log_key_name_exists_message(key: str) -> str:
    return f"Key name '{key}' already exists."

def get_wrong_argument_message() -> str:
    return "Invalid arguments. Usage: /addkey <days> <key>"

def get_key_added_message(key: str, days: int) -> str:
    return f"Key '{key}' added successfully for {days} days."
