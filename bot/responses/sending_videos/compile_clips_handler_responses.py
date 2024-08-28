def get_invalid_args_count_message() -> str:
    return "🔄 Proszę podać indeksy cytatów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów."


def get_no_previous_search_results_message() -> str:
    return "🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj."


def get_no_matching_segments_found_message() -> str:
    return "❌ Nie znaleziono pasujących cytatów do kompilacji.❌"


def get_invalid_range_message(index: str) -> str:
    return f"⚠️ Podano nieprawidłowy zakres cytatów: {index} ⚠️"


def get_invalid_index_message(index: str) -> str:
    return f"⚠️ Podano nieprawidłowy indeks cytatu: {index} ⚠️"


def get_compilation_success_message(username: str) -> str:
    return f"Compiled clip sent to user '{username}' and temporary files removed."


def get_log_no_previous_search_results_message() -> str:
    return "No previous search results found for user."


def get_log_no_matching_segments_found_message() -> str:
    return "No matching segments found for compilation."


def get_max_clips_exceeded_message() -> str:
    return "❌ Przekroczono maksymalną liczbę klipów do skompilowania.❌"


def get_clip_time_message() -> str:
    return "❌ Przekroczono maksymalny czas trwania kompilacji.❌"
