import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.handlers.responses.my_clips_handler_responses import (
    format_myclips_response,
    get_log_no_saved_clips_message,
    get_log_saved_clips_sent_message,
    get_no_saved_clips_message,
)
from bot.utils.database import DatabaseManager


class MyClipsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['mojeklipy', 'myclips', 'mk']

    async def _do_handle(self, message: Message) -> None:
        username = message.from_user.username

        clips = await DatabaseManager.get_saved_clips(username)
        if not clips:
            return await self.__reply_no_saved_clips(message, username)

        await message.answer(format_myclips_response(clips, username), parse_mode='Markdown')
        await self._log_system_message(logging.INFO, get_log_saved_clips_sent_message(username))

    async def __reply_no_saved_clips(self, message: Message, username: str) -> None:
        await message.answer(get_no_saved_clips_message())
        await self._log_system_message(logging.INFO, get_log_no_saved_clips_message(username))
