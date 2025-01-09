def get_log_no_previous_search_message() -> str:
    return "No previous search results found for user."


def get_log_invalid_segment_number_message(segment_number: int) -> str:
    return f"Invalid segment number provided by user: {segment_number}"


def get_log_segment_selected_message(segment_id: str, username: str) -> str:
    return f"Segment {segment_id} selected by user '{username}'."
