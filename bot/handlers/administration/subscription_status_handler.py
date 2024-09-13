from datetime import date
import logging
from typing import (
    List,
    Optional,
    Tuple,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.subscription_status_handler_responses import (
    format_subscription_status_response,
    get_log_no_active_subscription_message,
    get_log_subscription_status_sent_message,
    get_no_subscription_message,
)


class SubscriptionStatusHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["subskrypcja", "subscription", "sub"]

    async def _do_handle(self, message: Message) -> None:
        subscription_status = await self.__get_subscription_status(message.from_user.id)

        if subscription_status is None:
            return await self.__reply_no_subscription(message)

        subscription_end, days_remaining = subscription_status
        user_name = message.from_user.username or message.from_user.full_name
        response = format_subscription_status_response(user_name, subscription_end, days_remaining)

        await message.answer(response, parse_mode="Markdown")
        await self._log_system_message(logging.INFO, get_log_subscription_status_sent_message(user_name))

    @staticmethod
    async def __get_subscription_status(user_id: int) -> Optional[Tuple[date, int]]:
        subscription_end = await DatabaseManager.get_user_subscription(user_id)
        if subscription_end is None:
            return None
        days_remaining = (subscription_end - date.today()).days
        return subscription_end, days_remaining

    async def __reply_no_subscription(self, message: Message) -> None:
        user_name = message.from_user.username or message.from_user.full_name
        await message.answer(get_no_subscription_message())
        await self._log_system_message(logging.INFO, get_log_no_active_subscription_message(user_name))
