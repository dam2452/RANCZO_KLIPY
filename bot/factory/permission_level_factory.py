from abc import (
    ABC,
    abstractmethod,
)
import logging
from typing import (
    List,
    Tuple,
)

from aiogram import (
    Bot,
    Dispatcher,
)

from bot.handlers import *  # pylint: disable=wildcard-import, unused-wildcard-import
from bot.middlewares import *  # pylint: disable=wildcard-import, unused-wildcard-import


class PermissionLevelFactory(ABC):
    def __init__(self, logger: logging.Logger, bot: Bot):
        self._logger = logger
        self._bot = bot

    def create_and_register(self, dp: Dispatcher) -> None:
        handlers, middlewares = self.create()

        for handler in handlers:
            handler.register(dp)

        self._logger.info(f"{self.__class__.__name__} handlers registered")

        for middleware in middlewares:
            dp.message.middleware.register(middleware)

        self._logger.info(f"{self.__class__.__name__} middlewares registered")

    def create(self) -> Tuple[List[BotMessageHandler], List[BotMiddleware]]:
        handlers = self.create_handlers()
        middlewares = self.create_middlewares(self.get_permission_level_commands(handlers))
        return handlers, middlewares

    @staticmethod
    def get_permission_level_commands(handlers: List[BotMessageHandler]) -> List[str]:
        return [command for handler in handlers for command in handler.get_commands()]

    @abstractmethod
    def create_handlers(self) -> List[BotMessageHandler]:
        pass

    @abstractmethod
    def create_middlewares(self, commands: List[str]) -> List[BotMiddleware]:
        pass
