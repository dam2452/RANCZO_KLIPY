import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.admin_help_handler_responses import (
    get_admin_help_message,
    get_admin_shortcuts_message,
    get_message_sent_log_message,
)


class AdminHelpHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["admin"]

    async def _do_handle(self, message: Message) -> None:
        if "skroty" in message.text.lower():
            await self.__reply_admin_shortcuts(message)
        else:
            await self.__reply_admin_help(message)

    async def __reply_admin_help(self, message: Message) -> None:
        await message.answer(get_admin_help_message(), parse_mode="Markdown")
        await self._log_system_message(logging.INFO, get_message_sent_log_message(message.from_user.username))

    async def __reply_admin_shortcuts(self, message: Message) -> None:
        await message.answer(get_admin_shortcuts_message(), parse_mode="Markdown")
        await self._log_system_message(logging.INFO, f"Admin shortcuts sent to {message.from_user.username}")
