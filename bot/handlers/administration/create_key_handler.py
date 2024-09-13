from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.create_key_handler_responses import (
    get_create_key_success_message,
    get_create_key_usage_message,
)


class CreateKeyHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["addkey", "addk"]

    async def _do_handle(self, message: Message) -> None:
        args = message.text.split()
        if len(args) < 3:
            await message.answer(get_create_key_usage_message())
            return

        days = int(args[1])
        name = " ".join(args[2:])

        await DatabaseManager.create_subscription_key(days, name)
        await message.answer(get_create_key_success_message(days, name))
