from typing import (
    Dict,
    List,
    Union,
)


def format_episode_list_response(season: int, episodes: List[Dict[str, Union[str, int]]]) -> str:
    response = f"📃 Lista odcinków dla sezonu {season}:\n\n```\n"
    for episode in episodes:
        absolute_episode_number = episode["episode_number"] % 13
        if absolute_episode_number == 0:
            absolute_episode_number = 13
        formatted_viewership = f"{episode["viewership"]:,}".replace(",", ".")

        response += f"🎬 {episode["title"]}: S{season:02d}E{absolute_episode_number:02d} ({episode["episode_number"]}) \n"
        response += f"📅 Data premiery: {episode["premiere_date"]}\n"
        response += f"👀 Oglądalność: {formatted_viewership}\n\n"
    response += "```"
    return response


def get_no_episodes_found_message(season: int) -> str:
    return f"❌ Nie znaleziono odcinków dla sezonu {season}."


def get_log_no_episodes_found_message(season: int) -> str:
    return f"No episodes found for season {season}."


def get_log_episode_list_sent_message(season: int, username: str) -> str:
    return f"Sent episode list for season {season} to user '{username}'."


def get_invalid_args_count_message() -> str:
    return "📋 Podaj poprawną komendę w formacie: /listaodcinków <sezon>. Przykład: /listaodcinków 2"
