from typing import (
    Dict,
    List,
    Union,
)

from tabulate import tabulate

from bot.utils.functions import format_segment


def get_no_previous_search_results_message() -> str:
    return "🔍 Nie znaleziono wcześniejszych wyników wyszukiwania."


def get_log_no_previous_search_results_message(chat_id: int) -> str:
    return f"No previous search results found for chat ID {chat_id}."


def format_search_list_response(search_term: str, segments: List[Dict[str, Union[str, int]]]) -> str:
    response = f"🔍 Znaleziono {len(segments)} pasujących segmentów dla zapytania '{search_term}':\n"
    segment_lines = []

    for i, segment in enumerate(segments, start=1):
        segment_info = format_segment(segment)
        segment_lines.append([i, segment_info.episode_formatted, segment_info.episode_title, segment_info.time_formatted])

    table = tabulate(
        segment_lines, headers=["#", "Odcinek", "Tytuł", "Czas"], tablefmt="pipe", colalign=("left", "center", "left", "right"),
    )
    response += f"{table}\n"

    return response


def get_log_search_results_sent_message(search_term: str, username: str) -> str:
    return f"List of search results for term '{search_term}' sent to user {username}."
