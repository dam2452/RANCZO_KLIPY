def get_no_segments_found_message() -> str:
    return "❌ Nie znaleziono pasujących cytatów.❌"


def get_extraction_failure_message() -> str:
    return "⚠️ Nie udało się wyodrębnić klipu wideo.⚠️"


def get_no_quote_provided_message() -> str:
    return "🔎 Podaj cytat, który chcesz znaleźć. Przykład: /klip Nie szkoda panu tego pięknego gabinetu?"


def get_log_no_segments_found_message(quote: str) -> str:
    return f"No segments found for quote: '{quote}'"


def get_log_extraction_failure_message(exception: Exception) -> str:
    return f"Failed to extract video clip: {exception}"


def get_log_segment_saved_message(chat_id: int) -> str:
    return f"Segment saved as last selected for chat ID '{chat_id}'"


def get_log_clip_success_message(username: str) -> str:
    return f"Video clip extracted successfully for user '{username}'."
