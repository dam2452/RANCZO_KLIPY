import logging
from typing import (
    Callable,
    Dict,
    List,
    Optional,
)

from aiogram import (
    BaseMiddleware,
    Bot,
)
from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.start_handler_responses import (
    get_basic_message,
    get_edycja_message,
    get_full_message,
    get_invalid_command_message,
    get_lista_message,
    get_log_message_sent,
    get_log_received_start_command,
    get_raportowanie_message,
    get_subskrypcje_message,
    get_wyszukiwanie_message,
    get_zarzadzanie_message,
)


class StartHandler(BotMessageHandler):
    def __init__(self, bot: Bot, logger: logging.Logger, middlewares: Optional[List[BaseMiddleware]] = None):
        self.__RESPONSES: Dict[str, Callable[[], str]] = {
            "lista": get_lista_message,
            "all": get_full_message,
            "wyszukiwanie": get_wyszukiwanie_message,
            "edycja": get_edycja_message,
            "zarzadzanie": get_zarzadzanie_message,
            "raportowanie": get_raportowanie_message,
            "subskrypcje": get_subskrypcje_message,
        }

        super().__init__(bot, logger, middlewares)

    def get_commands(self) -> List[str]:
        return ['start', 's', 'help', 'h']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        await self._log_system_message(logging.INFO, get_log_received_start_command(message.from_user.username, message.text))

        if len(content) == 1:
            await self.__send_message(message, get_basic_message())
        elif len(content) == 2:
            if content[1] in self.__RESPONSES:
                await self.__send_message(message, self.__RESPONSES[content[1]]())
            else:
                await self.__send_message(message, get_invalid_command_message())

    async def __send_message(self, message: Message, text: str) -> None:
        await message.answer(text, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, get_log_message_sent(message.from_user.username, text))
