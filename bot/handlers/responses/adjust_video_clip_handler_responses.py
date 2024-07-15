def get_no_previous_searches_message() -> str:
    return "🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj."


def get_no_quotes_selected_message() -> str:
    return "⚠️ Najpierw wybierz cytat za pomocą /klip.⚠️"


def get_invalid_args_count_message() -> str:
    return "📝 Podaj czas w formacie `<float> <float>` lub `<index> <float> <float>`. Przykład: /dostosuj 10.5 -15.2 lub /dostosuj 1 10.5 -15.2"


def get_invalid_interval_message() -> str:
    return "⚠️ Czas zakończenia musi być późniejszy niż czas rozpoczęcia.⚠️"


def get_invalid_segment_index_message() -> str:
    return "⚠️ Podano nieprawidłowy indeks segmentu.⚠️"


def get_invalid_video_path_message() -> str:
    return "⚠️ Nieprawidłowa ścieżka do wideo.⚠️"


def get_extraction_failure_message(exception: Exception) -> str:
    return f"⚠️ Nie udało się zmienić klipu wideo: {exception}"
