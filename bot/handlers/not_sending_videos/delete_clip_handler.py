import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.delete_clip_handler_responses import (
    get_clip_deleted_message,
    get_clip_name_length_exceeded_message,
    get_clip_not_exist_message,
    get_invalid_args_count_message,
    get_log_clip_deleted_message,
    get_log_clip_not_exist_message,
)
from bot.settings import settings


class DeleteClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["usuńklip", "usunklip", "deleteclip", "uk"]

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_invalid_args_count_message())
            return
        clip_name = " ".join(content[1:])

        if len(clip_name) > settings.MAX_CLIP_NAME_LENGTH:
            await message.answer(get_clip_name_length_exceeded_message())
            return

        result = await DatabaseManager.delete_clip(message.from_user.id, clip_name)

        if result == "DELETE 0":
            await self.__reply_clip_not_exist(message, clip_name, message.from_user.username)
        else:
            await self.__reply_clip_deleted(message, clip_name, message.from_user.username)

    async def __reply_clip_not_exist(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(get_clip_not_exist_message(clip_name))
        await self._log_system_message(logging.INFO, get_log_clip_not_exist_message(clip_name, username))

    async def __reply_clip_deleted(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(get_clip_deleted_message(clip_name))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_deleted_message(clip_name, username),
        )
