import logging
from typing import (
    List,
    Optional,
)

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.episode_list_handler_responses import (
    format_episode_list_response,
    get_invalid_args_count_message,
    get_log_episode_list_sent_message,
    get_log_no_episodes_found_message,
    get_no_episodes_found_message,
)
from bot.search.transcription_finder import TranscriptionFinder


class EpisodeListHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["odcinki", "episodes", "o"]

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) != 2:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        season = int(content[1])
        episodes = await TranscriptionFinder.find_episodes_by_season(season, self._logger)
        if not episodes:
            return await self.__reply_no_episodes_found(message, season)

        response_parts = self.__split_message(format_episode_list_response(season, episodes))

        for part in response_parts:
            await message.answer(part, parse_mode="Markdown")

        await self._log_system_message(
            logging.INFO,
            get_log_episode_list_sent_message(season, message.from_user.username),
        )

    @staticmethod
    def __split_message(message: str, max_length: int = 4096) -> Optional[List[str]]:
        parts = []
        while len(message) > max_length:
            split_at = message.rfind("\n", 0, max_length)
            if split_at == -1:
                split_at = max_length
            parts.append(message[:split_at])
            message = message[split_at:].lstrip()
        parts.append(message)
        return parts

    async def __reply_no_episodes_found(self, message: Message, season: int) -> None:
        await message.answer(get_no_episodes_found_message(season))
        await self._log_system_message(logging.INFO, get_log_no_episodes_found_message(season))
