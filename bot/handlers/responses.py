from datetime import date
from typing import (
    Dict,
    List,
)


def convert_number_to_emoji(number: int) -> str:
    return ''.join(number_to_emoji.get(digit, digit) for digit in str(number))


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


def format_subscription_status_response(username: str, subscription_end: date, days_remaining: int) -> str:
    return f"""
✨ **Status Twojej subskrypcji** ✨

👤 **Użytkownik:** {username}
📅 **Data zakończenia:** {subscription_end}
⏳ **Pozostało dni:** {days_remaining}

Dzięki za wsparcie projektu! 🎉
"""


def format_myclips_response(clips, username):
    response = "🎬 Twoje Zapisane Klipy 🎬\n\n"
    response += f"🎥 Użytkownik: @{username}\n\n"
    clip_lines = []

    for idx, (clip_name, start_time, end_time, season, episode_number, is_compilation) in enumerate(clips, start=1):
        length = end_time - start_time if end_time and start_time is not None else None
        if length:
            minutes, seconds = divmod(length, 60)
            length_str = f"{minutes}m{seconds}s" if minutes else f"{seconds}s"
        else:
            length_str = "Brak danych"

        if is_compilation or season is None or episode_number is None:
            season_episode = "Kompilacja"
        else:
            episode_number_mod = (episode_number - 1) % 13 + 1
            season_episode = f"S{season:02d}E{episode_number_mod:02d}"

        emoji_index = convert_number_to_emoji(idx)
        line1 = f"{emoji_index} | 📺 {season_episode} | 🕒 {length_str}"
        line2 = f"👉 {clip_name}"
        clip_lines.append(f"{line1} \n{line2}")

    response += "```\n" + "\n\n".join(clip_lines) + "\n```"
    return response


def format_episode_list_response(season: int, episodes: List[dict]) -> str:
    response = f"📃 Lista odcinków dla sezonu {season}:\n\n```\n"
    for episode in episodes:
        absolute_episode_number = episode['episode_number'] % 13
        if absolute_episode_number == 0:
            absolute_episode_number = 13
        formatted_viewership = f"{episode['viewership']:,}".replace(',', '.')

        response += f"🎬 {episode['title']}: S{season:02d}E{absolute_episode_number:02d} ({episode['episode_number']}) \n"
        response += f"📅 Data premiery: {episode['premiere_date']}\n"
        response += f"👀 Oglądalność: {formatted_viewership}\n\n"
    response += "```"
    return response
