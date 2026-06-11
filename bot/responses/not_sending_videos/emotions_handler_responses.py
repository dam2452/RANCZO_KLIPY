from typing import List

from bot.responses.bot_response import BotResponse
from bot.search.video_frames.character_finder import _EMOTION_NAMES as _EMOTIONS
from bot.types import (
    EmotionInfo,
    Language,
)
from bot.utils.functions import convert_number_to_emoji


def format_emotions_list(emotions: List[EmotionInfo], lang: Language = "pl") -> str:
    if not emotions:
        return get_no_emotions_message(lang)
    if lang == "en":
        lines = [
            f"{convert_number_to_emoji(i + 1)}  {e['label_en']} ({e['label_pl']})"
            for i, e in enumerate(emotions)
        ]
        body = f"Total: {convert_number_to_emoji(len(emotions))} emotions\n\n" + "\n".join(lines)
        return BotResponse.info("AVAILABLE EMOTIONS", body)
    lines = [
        f"{convert_number_to_emoji(i + 1)}  {e['label_pl']} ({e['label_en']})"
        for i, e in enumerate(emotions)
    ]
    body = f"Łącznie: {convert_number_to_emoji(len(emotions))} emocji\n\n" + "\n".join(lines)
    return BotResponse.info("DOSTĘPNE EMOCJE", body)


def get_no_emotions_message(lang: Language = "pl") -> str:
    if lang == "en":
        return BotResponse.warning("NO DATA", "No emotion data in the index.")
    return BotResponse.warning("BRAK DANYCH", "Brak danych o emocjach w indeksie.")


def get_invalid_args_count_message() -> str:
    return BotResponse.usage(
        command="emocje",
        error_title="ZA DUŻO ARGUMENTÓW",
        usage_syntax="",
        params=[],
        example="/emocje",
    )


def get_log_emotions_listed_message(count: int, username: str) -> str:
    return f"Emotions list ({count} items) sent to user {username}."
