import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.my_clips_handler_responses import (
    format_myclips_response,
    get_log_no_saved_clips_message,
    get_log_saved_clips_sent_message,
    get_no_saved_clips_message,
)


class MyClipsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["mojeklipy", "myclips", "mk"]

    async def is_any_validation_failed(self, message: Message) -> bool:
        return False
    async def _do_handle(self, message: Message) -> None:
        clips = await DatabaseManager.get_saved_clips(message.from_user.id)
        if not clips:
            return await self.__reply_no_saved_clips(message)

        await self._answer_markdown(message , format_myclips_response(clips, message.from_user.username, message.from_user.full_name))
        await self._log_system_message(logging.INFO, get_log_saved_clips_sent_message(message.from_user.username))

    async def __reply_no_saved_clips(self, message: Message) -> None:
        await message.answer(get_no_saved_clips_message())
        await self._log_system_message(logging.INFO, get_log_no_saved_clips_message(message.from_user.username))
