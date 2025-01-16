import json
import logging
from pathlib import Path
from typing import (
    Awaitable,
    Callable,
    List,
    Optional,
    Tuple,
)

from aiogram.types import Message

from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.not_sending_videos.episode_list_handler_responses import (
    format_episode_list_response,
    get_log_episode_list_sent_message,
    get_log_no_episodes_found_message,
    get_season_11_petition_message,
)
from bot.search.transcription_finder import TranscriptionFinder
from bot.settings import settings as s

isSeasonCustomFn = Callable[[json], bool]
onCustomSeasonFn = Callable[[Message], Awaitable[None]]

class EpisodeListHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["odcinki", "episodes", "o"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [self.__check_argument_count]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, await self.get_response(RK.INVALID_ARGS_COUNT),
        )

    async def _do_handle(self, message: Message) -> None:
        season = int(message.text.split()[1])
        season_info = await TranscriptionFinder.get_season_details_from_elastic(logger=self._logger)
        episodes = await TranscriptionFinder.find_episodes_by_season(season, self._logger)

        context = {
            "season": season,
            "specialized_table": s.SPECIALIZED_TABLE,
            "episodes": episodes,
        }

        if await self.__check_easter_eggs(context, message):
            return

        if not episodes:
            return await self.__reply_no_episodes_found(message, season)

        response_parts = self.__split_message(format_episode_list_response(season, episodes, season_info))
        for part in response_parts:
            await self._answer_markdown(message, part)

        await self._log_system_message(
            logging.INFO,
            get_log_episode_list_sent_message(season, message.from_user.username),
        )

    async def __reply_no_episodes_found(self, message: Message, season: int) -> None:
        await self._answer(
            message, await self.get_response(RK.NO_EPISODES_FOUND, args=[str(season)]),
        )
        await self._log_system_message(logging.INFO, get_log_no_episodes_found_message(season))

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

    async def __handle_ranczo_season_11(self, message: Message) -> None:
        image_path = Path("Ranczo_Sezon11.png")
        with image_path.open("rb") as image_file:
            image_bytes = image_file.read()
        await self._answer_photo(message, image_bytes, image_path, caption=get_season_11_petition_message())

    @staticmethod
    def __is_ranczo_season_11(context: json) -> bool:
        return (
            context["season"] == 11
            and context["specialized_table"] == "ranczo_messages"
        )

    def __get_easter_eggs(self) -> List[Tuple[isSeasonCustomFn, onCustomSeasonFn]]:
        return [
            (self.__is_ranczo_season_11, self.__handle_ranczo_season_11),
        ]

    async def __check_easter_eggs(self, context: json, message: Message) -> bool:
        for predicate, callback in self.__get_easter_eggs():
            if predicate(context):
                await callback(message)
                return True
        return False
