def get_invalid_args_count_message() -> str:
    return "🔄 Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów."


def get_no_previous_search_results_message() -> str:
    return "🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj."


def get_no_matching_segments_found_message() -> str:
    return "❌ Nie znaleziono pasujących segmentów do kompilacji.❌"


def get_invalid_range_message(index: str) -> str:
    return f"⚠️ Podano nieprawidłowy zakres segmentów: {index} ⚠️"


def get_invalid_index_message(index: str) -> str:
    return f"⚠️ Podano nieprawidłowy indeks segmentu: {index} ⚠️"


def get_compilation_success_message(username: str) -> str:
    return f"Compiled clip sent to user '{username}' and temporary files removed."


def get_log_no_previous_search_results_message() -> str:
    return "No previous search results found for user."


def get_log_no_matching_segments_found_message() -> str:
    return "No matching segments found for compilation."
