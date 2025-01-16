import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.not_sending_videos.my_clips_handler_responses import (
    format_myclips_response,
    get_log_no_saved_clips_message,
    get_log_saved_clips_sent_message,
)
from bot.search.transcription_finder import TranscriptionFinder


class MyClipsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["mojeklipy", "myclips", "mk"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return []
    async def _do_handle(self, message: Message) -> None:
        clips = await DatabaseManager.get_saved_clips(message.from_user.id)
        if not clips:
            return await self.__reply_no_saved_clips(message)

        season_info = await TranscriptionFinder.get_season_details_from_elastic(
            logger=self._logger,
        )

        await self._answer_markdown(
            message , await format_myclips_response(
                clips=clips,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
                season_info=season_info,
            ),
        )
        await self._log_system_message(logging.INFO, get_log_saved_clips_sent_message(message.from_user.username))

    async def __reply_no_saved_clips(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.NO_SAVED_CLIPS))
        await self._log_system_message(logging.INFO, get_log_no_saved_clips_message(message.from_user.username))
