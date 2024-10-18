import logging
from typing import (
    List,
    Optional,
)

from aiogram.types import (
    BufferedInputFile,
    Message,
)

from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.not_sending_videos.episode_list_handler_responses import (
    format_episode_list_response,
    get_invalid_args_count_message,
    get_log_episode_list_sent_message,
    get_log_no_episodes_found_message,
    get_no_episodes_found_message,
    get_season_11_petition_message,
)
from bot.search.transcription_finder import TranscriptionFinder


class EpisodeListHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["odcinki", "episodes", "o"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__validate_argument_count,
        ]

    async def __validate_argument_count(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) != 2:
            await self._reply_invalid_args_count(message, get_invalid_args_count_message())
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        season = int(message.text.split()[1])

        if season == 11:
            return await self.__handle_season_11(message)

        episodes = await TranscriptionFinder.find_episodes_by_season(season, self._logger)
        if not episodes:
            return await self.__reply_no_episodes_found(message, season)

        response_parts = self.__split_message(format_episode_list_response(season, episodes))

        for part in response_parts:
            await self._answer_markdown(message , part)

        await self._log_system_message(
            logging.INFO,
            get_log_episode_list_sent_message(season, message.from_user.username),
        )
    @staticmethod
    async def __handle_season_11(message: Message) -> None:
        image_path = "Ranczo_Sezon11.png"
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            await message.answer_photo(
                photo=BufferedInputFile(image_bytes, image_path),
                caption=get_season_11_petition_message(),
                show_caption_above_media=True,
                parse_mode="Markdown",
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
