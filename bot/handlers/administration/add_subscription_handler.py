from datetime import date
import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.add_subscription_handler_responses import (
    get_subscription_error_log_message,
    get_subscription_log_message,
)


class AddSubscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["addsubscription", "addsub"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__validate_user_id_and_days,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 3, await self.get_response(RK.NO_USER_ID_PROVIDED))

    async def __validate_user_id_and_days(self, message: Message) -> bool:
        content = message.text.split()
        if not content[1].isdigit() or not content[2].isdigit():
            await self._reply_invalid_args_count(message, await self.get_response(RK.NO_USER_ID_PROVIDED))
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        user_id = int(message.text.split()[1])
        days = int(message.text.split()[2])

        new_end_date = await DatabaseManager.add_subscription(user_id, days)
        if new_end_date is None:
            return await self.__reply_subscription_error(message)

        await self.__reply_subscription_extended(message, user_id, new_end_date)

    async def __reply_subscription_extended(self, message: Message, user_id: int, new_end_date: date) -> None:
        response = await self.get_response(RK.SUBSCRIPTION_EXTENDED, [str(user_id), str(new_end_date)])
        await self._answer(message, response)
        await self._log_system_message(
            logging.INFO,
            get_subscription_log_message(str(user_id), message.from_user.username),
        )

    async def __reply_subscription_error(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.SUBSCRIPTION_ERROR))
        await self._log_system_message(logging.ERROR, get_subscription_error_log_message())
