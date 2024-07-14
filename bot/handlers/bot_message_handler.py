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

from bot.utils.database import DatabaseManager


class DummyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        raise Exception("tbd: zmienic na BotMiddleware, wyniesc do folderu odpowiedniego z tego pliku i uzyc jako baza obecnych")


class BotMessageHandler(ABC):
    __LOG_LEVELS: Dict[int, str] = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

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
        try:
            await self._do_handle(message)
        except Exception as e:  # pylint: disable=broad-exception-caught
            await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
            await self._log_system_message(logging.ERROR, f"Error in {self.get_action_name()} for user '{message.from_user.username}': {e}")

    async def _log_system_message(self, level: int, message: str) -> None:
        self._logger.log(level, message)
        await DatabaseManager.log_system_message(self.__LOG_LEVELS[level], message)

    async def _log_user_activity(self, username: str, message: str) -> None:
        await DatabaseManager.log_user_activity(username, message)
        await self._log_system_message(logging.INFO, f"User '{username}' performed action: {message}")

    async def _reply_invalid_args_count(
        self,
        message: Message,
        response: str,
    ) -> None:
        await message.answer(response)
        await self._log_system_message(logging.INFO, f"Incorrect command ({self.get_action_name()}) format provided by user.")

    def get_action_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def get_commands(self) -> List[str]:
        pass

    @abstractmethod
    async def _do_handle(self, message: Message) -> None:
        pass
