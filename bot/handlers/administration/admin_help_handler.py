import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.admin_help_handler_responses import get_admin_help_message


class AdminHelpHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['admin']

    async def _do_handle(self, message: Message) -> None:
        await self.__reply_admin_help(message)

    #fixme do responses
    async def __reply_admin_help(self, message: Message) -> None:
        await message.answer(get_admin_help_message(), parse_mode='Markdown')
        await self._log_system_message(logging.INFO, f"Admin help message sent to user '{message.from_user.username}'.")
