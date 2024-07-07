from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler


class AdjustVideoClipHandler(BotMessageHandler):
    async def handle(self, message: Message) -> None:
        pass

    def get_commands(self) -> List[str]:
        return ['dostosuj', 'adjust', 'd']
