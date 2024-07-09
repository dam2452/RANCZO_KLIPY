import logging
from datetime import date
from typing import (
    List,
    Optional,
    Tuple,
)

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.database import DatabaseManager


class UserManager: #fixme to też chyba do wywalenia wgl do osobnego pliku bo admin.py też z czegoś podbnego korzsyta a tak prosto z bazy ciągnąć bez żadnego checka to nwm
    @staticmethod
    async def get_subscription_status(username: str) -> Optional[Tuple[date, int]]:
        subscription_end = await DatabaseManager.get_user_subscription(username)
        if subscription_end is None:
            return None
        days_remaining = (subscription_end - date.today()).days
        return subscription_end, days_remaining


class SubscriptionStatusHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['subskrypcja', 'subscription', 'sub']

    def get_action_name(self) -> str:
        return "check_subscription"

    async def _do_handle(self, message: Message) -> None:
        username = message.from_user.username
        subscription_status = await UserManager.get_subscription_status(username)

        if subscription_status is None:
            return await self.__reply_no_subscription(message)

        subscription_end, days_remaining = subscription_status
        response = f"""
✨ **Status Twojej subskrypcji** ✨

👤 **Użytkownik:** {username}
📅 **Data zakończenia:** {subscription_end}
⏳ **Pozostało dni:** {days_remaining}

Dzięki za wsparcie projektu! 🎉
"""
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, f"Subscription status sent to user '{username}'.")

    async def __reply_no_subscription(self, message: Message) -> None:
        await message.answer("🚫 Nie masz aktywnej subskrypcji.🚫")
        await self._log_system_message(logging.INFO, f"No active subscription found for user '{message.from_user.username}'.")