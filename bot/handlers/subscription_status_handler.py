from datetime import date
import logging
from typing import (
    List,
    Optional,
    Tuple,
)

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.database import DatabaseManager
from bot.utils.responses import format_subscription_status_response


class SubscriptionStatusHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['subskrypcja', 'subscription', 'sub']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/subskrypcja {message.text}")
        username = message.from_user.username
        subscription_status = await self.__get_subscription_status(username)

        if subscription_status is None:
            return await self.__reply_no_subscription(message)

        subscription_end, days_remaining = subscription_status
        response = format_subscription_status_response(username, subscription_end, days_remaining)

        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, f"Subscription status sent to user '{username}'.")

    @staticmethod
    async def __get_subscription_status(username: str) -> Optional[Tuple[date, int]]:
        subscription_end = await DatabaseManager.get_user_subscription(username)
        if subscription_end is None:
            return None
        days_remaining = (subscription_end - date.today()).days
        return subscription_end, days_remaining

    async def __reply_no_subscription(self, message: Message) -> None:
        await message.answer("🚫 Nie masz aktywnej subskrypcji.🚫")
        await self._log_system_message(logging.INFO, f"No active subscription found for user '{message.from_user.username}'.")