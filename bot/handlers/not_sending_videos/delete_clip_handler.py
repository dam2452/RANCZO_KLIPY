import logging

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.delete_clip_handler_responses import (
    get_clip_deleted_message,
    get_clip_not_exist_message,
    get_invalid_args_count_message,
    get_log_clip_deleted_message,
    get_log_clip_not_exist_message,
)


class DeleteClipHandler(BotMessageHandler):

    def get_commands(self) -> list[str]:
        return ["usunklip", "deleteclip", "uk"]

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        if len(content) < 2 or not content[1].isdigit():
            await message.answer(get_invalid_args_count_message())
            return

        clip_number = int(content[1])

        user_clips = await DatabaseManager.get_saved_clips(message.chat.id)
        if clip_number < 1 or clip_number > len(user_clips):
            await message.answer(get_clip_not_exist_message(clip_number))
            await self._log_system_message(logging.INFO, get_log_clip_not_exist_message(clip_number, message.from_user.username))
            return

        clip_to_delete = user_clips[clip_number - 1]

        await DatabaseManager.delete_clip(message.chat.id, clip_to_delete.clip_name)

        await message.answer(get_clip_deleted_message(clip_to_delete.clip_name))
        await self._log_system_message(logging.INFO, get_log_clip_deleted_message(clip_to_delete.clip_name, message.from_user.username))
