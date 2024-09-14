from abc import (
    ABC,
    abstractmethod,
)
import logging
from typing import List

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.responses.bot_message_handler_responses import (
    get_general_error_message,
    get_invalid_args_count_message,
)
from bot.utils.log import (
    log_system_message,
    log_user_activity,
)


class BotMessageHandler(ABC):
    def __init__(self, bot: Bot, logger: logging.Logger):
        self._bot: Bot = bot
        self._logger: logging.Logger = logger

    def register(self, dp: Dispatcher) -> None:
        dp.message.register(self.handle, Command(commands=self.get_commands()))

    async def handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.id, message.text)

        try:
            await self._do_handle(message)
        except Exception as e:  # pylint: disable=broad-exception-caught
            await message.answer(get_general_error_message())
            await self._log_system_message(logging.ERROR, f"{type(e)} Error in {self.get_action_name()} for user '{message.from_user.id}': {e}")

        await DatabaseManager.log_command_usage(message.from_user.id)

    async def _log_system_message(self, level: int, message: str) -> None:
        await log_system_message(level, message, self._logger)

    async def _log_user_activity(self, user_id: int, message: str) -> None:
        await log_user_activity(user_id, message, self._logger)

    async def _reply_invalid_args_count(
        self,
        message: Message,
        response: str,
    ) -> None:
        await message.answer(response)
        await self._log_system_message(logging.INFO, get_invalid_args_count_message(self.get_action_name()))

    def get_action_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def get_commands(self) -> List[str]:
        pass

    @abstractmethod
    async def _do_handle(self, message: Message) -> None:
        pass
    @abstractmethod
    async def is_any_validation_failed(self, message: Message) -> bool:
        pass