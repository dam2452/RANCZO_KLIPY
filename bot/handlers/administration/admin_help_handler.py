import logging
from typing import List
from bot.database.response_keys import ResponseKey as RK
from aiogram.types import Message

from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.admin_help_handler_responses import (
    get_message_sent_log_message,
)


class AdminHelpHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["admin"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return []

    async def _do_handle(self, message: Message) -> None:
        keywords = ["skroty", "skróty", "skrot", "skrót"]
        if any(keyword in message.text.lower() for keyword in keywords):
            await self.__reply_admin_shortcuts(message)
        else:
            await self.__reply_admin_help(message)

    async def __reply_admin_help(self, message: Message) -> None:
        await self._answer_markdown(message, await self.get_response(RK.ADMIN_HELP))
        await self._log_system_message(logging.INFO, get_message_sent_log_message(message.from_user.username))

    async def __reply_admin_shortcuts(self, message: Message) -> None:
        await self._answer_markdown(message , await self.get_response(RK.ADMIN_SHORTCUTS))
        await self._log_system_message(logging.INFO, f"Admin shortcuts sent to {message.from_user.username}")
