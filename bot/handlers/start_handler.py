import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler

from responses import (
    get_basic_message,
    get_lista_message,
    get_full_message,
    get_wyszukiwanie_message,
    get_edycja_message,
    get_zarzadzanie_message,
    get_raportowanie_message,
    get_subskrypcje_message
)


class StartCommandHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['start', 's', 'help', 'h']

    def get_action_name(self) -> str:
        return "start_handler"

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/start {message.text}")
        username = message.from_user.username
        content = message.text.split()
        await self._log_system_message(logging.INFO,
                                       f"Received start command from user '{username}' with content: {message.text}")

        if len(content) == 1:
            await self._send_message(message, get_basic_message())
        elif len(content) == 2:
            if content[1] == 'lista':
                await self._send_message(message, get_lista_message())
            elif content[1] == 'all':
                await self._send_message(message, get_full_message())
            elif content[1] == 'wyszukiwanie':
                await self._send_message(message, get_wyszukiwanie_message())
            elif content[1] == 'edycja':
                await self._send_message(message, get_edycja_message())
            elif content[1] == 'zarządzanie':
                await self._send_message(message, get_zarzadzanie_message())
            elif content[1] == 'raportowanie':
                await self._send_message(message, get_raportowanie_message())
            elif content[1] == 'subskrypcje':
                await self._send_message(message, get_subskrypcje_message())

    async def _send_message(self, message: Message, text: str) -> None:
        await message.answer(text, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, f"Message sent to user '{message.from_user.username}': {text}")
