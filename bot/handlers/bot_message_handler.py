from abc import (
    ABC,
    abstractmethod,
)
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


class DummyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        raise Exception("tbd: zmienic na BotMiddleware, wyniesc do folderu odpowiedniego z tego pliku i uzyc jako baza obecnych")


class BotMessageHandler(ABC):
    def __init__(self, bot: Bot, middlewares: Optional[List[BaseMiddleware]] = None) -> None:
        self._bot = bot

        self._middlewares = middlewares if middlewares else [
            DummyMiddleware(),
            DummyMiddleware(),
            # todo
        ]

    def register(self, dp: Dispatcher) -> None:
        for middleware in self._middlewares:
            dp.message.middleware(middleware)

        dp.message.register(self.handle, Command(commands=self.get_commands()))

    @abstractmethod
    async def handle(self, message: Message) -> None:
        pass

    @abstractmethod
    def get_commands(self) -> List[str]:
        pass
