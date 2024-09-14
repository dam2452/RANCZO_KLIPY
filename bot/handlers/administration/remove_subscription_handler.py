import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.remove_subscription_handler_responses import (
    get_log_subscription_removed_message,
    get_no_username_provided_message,
    get_subscription_removed_message,
)


class RemoveSubscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["removesubscription", "rmsub"]

    async def is_any_validation_failed(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_no_username_provided_message())
            return True
        return False

    async def _do_handle(self, message: Message) -> None:
        username = message.text.split()[1]
        await DatabaseManager.remove_subscription(message.from_user.id)
        await self.__reply_subscription_removed(message, username)

    async def __reply_subscription_removed(self, message: Message, username: str) -> None:
        await message.answer(get_subscription_removed_message(username))
        await self._log_system_message(logging.INFO, get_log_subscription_removed_message(username, message.from_user.username))
