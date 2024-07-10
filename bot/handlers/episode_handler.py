import logging
from typing import List, Optional, Tuple

from aiogram.types import Message

from bot_message_handler import BotMessageHandler

from bot.utils.transcription_search import SearchTranscriptions
from responses import format_episode_list_response


def adjust_episode_number(absolute_episode: int) -> Optional[Tuple[int, int]]:  #fixme chyba powtorka
    """ Adjust the absolute episode number to season and episode format """
    season = (absolute_episode - 1) // 13 + 1
    episode = (absolute_episode - 1) % 13 + 1
    return season, episode


def split_message(message: str, max_length: int = 4096) -> Optional[List[str]]: #fixme to chyba wyjazd do utils.py ?
    parts = []
    while len(message) > max_length:
        split_at = message.rfind('\n', 0, max_length)
        if split_at == -1:
            split_at = max_length
        parts.append(message[:split_at])
        message = message[split_at:].lstrip()
    parts.append(message)
    return parts


class EpisodeListHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['odcinki', 'episodes', 'o']

    def get_action_name(self) -> str:
        return "episode_handler"

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/odcinki {message.text}")
        search_transcriptions = SearchTranscriptions(self._bot.get_dispatcher())  #fixme tak samo
        content = message.text.split()
        if len(content) != 2:
            await self.__reply_invalid_args_count(message)
            return

        season = int(content[1])
        episodes = await search_transcriptions.find_episodes_by_season(season)
        if not episodes:
            await self.__reply_no_episodes_found(message, season)
            return

        response_parts = split_message(format_episode_list_response(season, episodes))

        for part in response_parts:
            await message.answer(part + "```", parse_mode="Markdown")

        await self._log_system_message(logging.INFO,
                                       f"Sent episode list for season {season} to user '{message.from_user.username}'.")

    async def __reply_invalid_args_count(self, message: Message) -> None:
        await message.answer(
            "📋 Podaj poprawną komendę w formacie: /listaodcinków <sezon>. Przykład: /listaodcinków 2",
        )
        await self._log_system_message(logging.INFO, "Incorrect command format provided by user.")

    async def __reply_no_episodes_found(self, message: Message, season: int) -> None:
        await message.answer(f"❌ Nie znaleziono odcinków dla sezonu {season}.")
        await self._log_system_message(logging.INFO, f"No episodes found for season {season}.")
