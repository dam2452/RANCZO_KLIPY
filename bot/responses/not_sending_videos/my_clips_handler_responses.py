from typing import (
    Dict,
    List,
)

import asyncpg

number_to_emoji: Dict[str, str] = {
    '0': '0️⃣',
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣',
    '6': '6️⃣',
    '7': '7️⃣',
    '8': '8️⃣',
    '9': '9️⃣',
}


def convert_number_to_emoji(number: int) -> str:
    return ''.join(number_to_emoji.get(digit, digit) for digit in str(number))


def format_myclips_response(clips: List[asyncpg.Record], username: str) -> str:
    clip_lines = []

    for idx, (clip_name, _, _, duration, season, episode_number, is_compilation) in enumerate(clips, start=1):
        if duration:
            minutes, seconds = divmod(duration, 60)
            length_str = f"{minutes}m{seconds:.2f}s" if minutes else f"{seconds:.2f}s"
        else:
            length_str = "Brak danych"

        if is_compilation:
            minutes, seconds = divmod(duration, 60)
            length_str = f"{minutes}m{seconds:.2f}s" if minutes else f"{seconds:.2f}s"
            season_episode = "Kompilacja"
        else:
            episode_number_mod = (episode_number - 1) % 13 + 1
            season_episode = f"S{season:02d}E{episode_number_mod:02d}"

        clip_lines.append(f"{convert_number_to_emoji(idx)} | 📺 {season_episode} | 🕒 {length_str}\n👉 {clip_name}")

    return f"🎬 Twoje Zapisane Klipy 🎬\n\n🎥 Użytkownik: @{username}\n\n" + "```\n" + "\n\n".join(clip_lines) + "\n```"


def get_no_saved_clips_message() -> str:
    return "📭 Nie masz zapisanych klipów.📭"


def get_log_no_saved_clips_message(username: str) -> str:
    return f"No saved clips found for user: {username}"


def get_log_saved_clips_sent_message(username: str) -> str:
    return f"List of saved clips sent to user '{username}'."
