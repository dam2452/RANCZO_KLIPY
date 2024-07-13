import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import (
    get_whitelist_empty_message,
    create_whitelist_response,
)
from bot.utils.database import DatabaseManager


class ListWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['listwhitelist', 'listw']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, "/listwhitelist")
        users = await DatabaseManager.get_all_users()
        if not users:
            return await self.__reply_whitelist_empty(message)

        response = create_whitelist_response(users)
        await self.__reply_whitelist(message, response)

    async def __reply_whitelist_empty(self, message: Message) -> None:
        await message.answer(get_whitelist_empty_message())
        await self._log_system_message(logging.INFO, "Whitelist is empty.")

    async def __reply_whitelist(self, message: Message, response: str) -> None:
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, "Whitelist sent to user.")
