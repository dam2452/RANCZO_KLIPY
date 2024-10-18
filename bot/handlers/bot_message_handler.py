from abc import (
    ABC,
    abstractmethod,
)
import logging
from typing import (
    Awaitable,
    Callable,
    List,
)

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
from bot.responses.sending_videos.manual_clip_handler_responses import get_limit_exceeded_clip_duration_message
from bot.settings import settings
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
            for validator in self._get_validator_functions():
                if not await validator(message):
                    return
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

    @staticmethod
    async def _answer_markdown(message: Message, text: str) -> None:
        await message.answer(text, parse_mode="Markdown")

    @abstractmethod
    def _get_validator_functions(self) -> List[Callable[[Message], Awaitable[bool]]]:
        return []
    async def _handle_clip_duration_limit_exceeded(self, message: Message, clip_duration: float) -> bool:
        if not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and clip_duration > settings.MAX_CLIP_DURATION:
            await self._answer_markdown(message, get_limit_exceeded_clip_duration_message())
            return True

        return False
