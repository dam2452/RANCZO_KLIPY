import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.database import DatabaseManager
from bot.handlers.responses.delete_clip_handler_responses import (
    get_invalid_args_count_message,
    get_clip_not_exist_message,
    get_clip_deleted_message,
    get_log_clip_not_exist_message,
    get_log_clip_deleted_message
)


class DeleteClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['usunklip', 'deleteclip', 'uk']

    async def _do_handle(self, message: Message) -> None:
        command = self.get_commands()[0]
        await self._log_user_activity(message.from_user.username, f"/{command} {message.text}")
        username = message.from_user.username

        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        clip_name = command_parts[1]

        result = await DatabaseManager.delete_clip(username, clip_name)

        if result == "DELETE 0":
            await self.__reply_clip_not_exist(message, clip_name, username)
        else:
            await self.__reply_clip_deleted(message, clip_name, username)

    async def __reply_clip_not_exist(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(get_clip_not_exist_message(clip_name))
        await self._log_system_message(logging.INFO, get_log_clip_not_exist_message(clip_name, username))

    async def __reply_clip_deleted(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(get_clip_deleted_message(clip_name))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_deleted_message(clip_name, username),
        )
