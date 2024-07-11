import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler
from responses import format_myclips_response

from bot.utils.database import DatabaseManager


class ListClipsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['mojeklipy', 'myclips', 'mk']

    def get_action_name(self) -> str:
        return "myclips_handler"

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/mojeklipy {message.text}")
        username = message.from_user.username

        clips = await DatabaseManager.get_saved_clips(username)
        if not clips:
            await self.__reply_no_saved_clips(message, username)
            return

        response = format_myclips_response(clips, username)
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, f"List of saved clips sent to user '{username}'.")

    async def __reply_no_saved_clips(self, message: Message, username: str) -> None:
        await message.answer("📭 Nie masz zapisanych klipów.📭")
        await self._log_system_message(logging.INFO, f"No saved clips found for user: {username}")

