from bot.utils.episode import Episode


def get_invalid_args_count_message() -> str:
    return "📋 Podaj poprawną komendę w formacie: /manual <sezon_odcinek> <czas_start> <czas_koniec>. Przykład: /manual S02E10 20:30.11"


def get_incorrect_season_episode_format_message() -> str:
    return "❌ Błędny format sezonu i odcinka. Użyj formatu SxxExx. Przykład: S02E10"


def get_video_file_not_exist_message() -> str:
    return "❌ Plik wideo nie istnieje dla podanego sezonu i odcinka."


def get_incorrect_time_format_message() -> str:
    return "❌ Błędny format czasu. Użyj formatu MM:SS.ms. Przykład: 20:30.11"


def get_end_time_earlier_than_start_message() -> str:
    return "❌ Czas zakończenia musi być późniejszy niż czas rozpoczęcia."


def get_log_incorrect_season_episode_format_message() -> str:
    return "Incorrect season/episode format provided by user."


def get_log_video_file_not_exist_message(video_path: str) -> str:
    return f"Video file does not exist: {video_path}"


def get_log_incorrect_time_format_message() -> str:
    return "Incorrect time format provided by user."


def get_log_end_time_earlier_than_start_message() -> str:
    return "End time must be later than start time."


def get_log_clip_extracted_message(episode: Episode, start_seconds: float, end_seconds: float) -> str:
    return f"Clip extracted and sent for command: /manual {episode} {start_seconds} {end_seconds}"
