from abc import (
    ABC,
    abstractmethod,
)
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
)

from aiogram import (
    BaseMiddleware,
    Bot,
    Dispatcher,
)
from aiogram.filters import Command
from aiogram.types import (
    Message,
    TelegramObject,
)

from bot.handlers.responses.bot_message_handler_responses import (
    get_general_error_message,
    get_invalid_args_count_message,
)
from bot.utils.log import (
    log_system_message,
    log_user_activity,
)


class DummyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        raise Exception("tbd: zmienic na BotMiddleware, wyniesc do folderu odpowiedniego z tego pliku i uzyc jako baza obecnych")


class BotMessageHandler(ABC):
    def __init__(self, bot: Bot, middlewares: Optional[List[BaseMiddleware]] = None):
        self._bot: Bot = bot
        self._logger: logging.Logger = logging.getLogger(__name__)

        self._middlewares: List[DummyMiddleware] = middlewares if middlewares else [
            DummyMiddleware(),
            DummyMiddleware(),
            # todo
        ]

    def register(self, dp: Dispatcher) -> None:
        for middleware in self._middlewares:
            dp.message.middleware(middleware)

        dp.message.register(self.handle, Command(commands=self.get_commands()))

    async def handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/{self.get_commands()[0]} {message.text}")
        try:
            await self._do_handle(message)
        except Exception as e:  # pylint: disable=broad-exception-caught
            await message.answer(get_general_error_message())
            await self._log_system_message(logging.ERROR, f"Error in {self.get_action_name()} for user '{message.from_user.username}': {e}")

    async def _log_system_message(self, level: int, message: str) -> None:
        await log_system_message(level, message, self._logger)

    async def _log_user_activity(self, username: str, message: str) -> None:
        await log_user_activity(username, message, self._logger)

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
