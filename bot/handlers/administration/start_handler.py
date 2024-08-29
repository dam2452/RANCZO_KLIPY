import logging
from typing import (
    Callable,
    Dict,
    List,
)

from aiogram import Bot
from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.start_handler_responses import (
    get_basic_message,
    get_edycja_message,
    get_full_message,
    get_invalid_command_message,
    get_lista_message,
    get_log_received_start_command,
    get_log_start_message_sent,
    get_raportowanie_message,
    get_shortcuts_message,
    get_subskrypcje_message,
    get_wyszukiwanie_message,
    get_zarzadzanie_message,
)


class StartHandler(BotMessageHandler):
    def __init__(self, bot: Bot, logger: logging.Logger):
        self.__RESPONSES: Dict[str, Callable[[], str]] = {
            "lista": get_lista_message,
            "list": get_lista_message,
            "wszystko": get_full_message,
            "all": get_full_message,
            "wyszukiwanie": get_wyszukiwanie_message,
            "search": get_wyszukiwanie_message,
            "edycja": get_edycja_message,
            "edit": get_edycja_message,
            "zarzadzanie": get_zarzadzanie_message,
            "zarządzanie": get_zarzadzanie_message,
            "management": get_zarzadzanie_message,
            "raportowanie": get_raportowanie_message,
            "reporting": get_raportowanie_message,
            "subskrypcje": get_subskrypcje_message,
            "subscriptions": get_subskrypcje_message,
            "skroty": get_shortcuts_message,
            "skróty": get_shortcuts_message,
            "skrot": get_shortcuts_message,
            "skrót": get_shortcuts_message,
            "shortcuts": get_shortcuts_message,
        }
        super().__init__(bot, logger)

    def get_commands(self) -> List[str]:
        return ["start", "s", "help", "h", "pomoc"]

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        await self._log_system_message(logging.INFO, get_log_received_start_command(message.from_user.username, message.text))

        if len(content) == 1:
            await self.__send_message(message, get_basic_message())
        elif len(content) == 2:
            command = content[1].lower()
            response_func = self.__RESPONSES.get(command)
            if response_func:
                await self.__send_message(message, response_func())
            else:
                await self.__send_message(message, get_invalid_command_message())

    async def __send_message(self, message: Message, text: str) -> None:
        await message.answer(text, parse_mode="Markdown")
        await self._log_system_message(logging.INFO, get_log_start_message_sent(message.from_user.username))
