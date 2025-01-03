from bot.video.episode import Episode


def get_log_incorrect_season_episode_format_message() -> str:
    return "Incorrect season/episode format provided by user."


def get_log_video_file_not_exist_message(video_path: str) -> str:
    return f"Video file does not exist: {video_path}"


def get_log_incorrect_time_format_message() -> str:
    return "Incorrect time format provided by user."


def get_log_end_time_earlier_than_start_message() -> str:
    return "End time must be later than start time."


def get_log_clip_extracted_message(episode: Episode, start_seconds: float, end_seconds: float) -> str:
    return f"Clip extracted and sent for command: /wytnij {episode} {start_seconds} {end_seconds}"


