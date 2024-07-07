from abc import (
    ABC,
    abstractmethod,
)
from typing import List

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.filters import Command
from aiogram.types import Message


class BotMessageHandler(ABC):
    def __init__(self, bot: Bot):
        self._bot = bot

    def register(self, dp: Dispatcher) -> None:
        dp.message.register(self.handle, Command(commands=self.get_commands()))

    @abstractmethod
    async def handle(self, message: Message) -> None:
        pass

    @abstractmethod
    def get_commands(self) -> List[str]:
        pass
