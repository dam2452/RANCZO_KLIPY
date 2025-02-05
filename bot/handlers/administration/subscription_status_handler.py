from datetime import date
import logging
from typing import (
    List,
    Optional,
    Tuple,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.subscription_status_handler_responses import (
    get_log_no_active_subscription_message,
    get_log_subscription_status_sent_message,
)


class SubscriptionStatusHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["subskrypcja", "subscription", "sub"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return []

    async def _do_handle(self, message: Message) -> None:
        subscription_status = await self.__get_subscription_status(message.from_user.id)

        if subscription_status is None:
            return await self.__reply_no_subscription(message)

        subscription_end, days_remaining = subscription_status
        user_name = message.from_user.username or message.from_user.full_name
        response = await self.get_response(RK.SUBSCRIPTION_STATUS, [user_name, str(subscription_end), str(days_remaining)])

        await self._answer_markdown(message , response)
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
        await self._answer(message,await self.get_response(RK.NO_SUBSCRIPTION))
        await self._log_system_message(logging.INFO, get_log_no_active_subscription_message(user_name))
