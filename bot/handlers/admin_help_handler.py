import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import get_admin_help_message

class AdminHelpHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['admin']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, "/admin")
        await message.answer(get_admin_help_message(), parse_mode='Markdown')
        await self._log_system_message(logging.INFO, f"Admin help message sent to user '{message.from_user.username}'.")