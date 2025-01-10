import logging
from typing import (
    Callable,
    Dict,
    List,
)

from aiogram import Bot
from aiogram.types import Message

from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.start_handler_responses import (
    get_log_received_start_command,
    get_log_start_message_sent,
)
from bot.utils.functions import remove_diacritics_and_lowercase


class StartHandler(BotMessageHandler):
    def __init__(self, bot: Bot, logger: logging.Logger):
        self.__RESPONSES: Dict[str, Callable[[], str]] = {
            "lista": lambda: RK.LIST_MESSAGE,
            "list": lambda: RK.LIST_MESSAGE,
            "l": lambda: RK.LIST_MESSAGE,

            "wszystko": lambda: RK.ALL_MESSAGE,
            "all": lambda: RK.ALL_MESSAGE,
            "a": lambda: RK.ALL_MESSAGE,

            "wyszukiwanie": lambda: RK.SEARCH_MESSAGE,
            "search": lambda: RK.SEARCH_MESSAGE,
            "s": lambda: RK.SEARCH_MESSAGE,

            "edycja": lambda: RK.EDIT_MESSAGE,
            "edit": lambda: RK.EDIT_MESSAGE,
            "e": lambda: RK.EDIT_MESSAGE,

            "zarzadzanie": lambda: RK.MANAGEMENT_MESSAGE,
            "management": lambda: RK.MANAGEMENT_MESSAGE,
            "m": lambda: RK.MANAGEMENT_MESSAGE,

            "raportowanie": lambda: RK.REPORTING_MESSAGE,
            "reporting": lambda: RK.REPORTING_MESSAGE,
            "r": lambda: RK.REPORTING_MESSAGE,

            "subskrypcje": lambda: RK.SUBSCRIPTIONS_MESSAGE,
            "subscriptions": lambda: RK.SUBSCRIPTIONS_MESSAGE,
            "sub": lambda: RK.SUBSCRIPTIONS_MESSAGE,

            "skroty": lambda: RK.SHORTCUTS_MESSAGE,
            "shortcuts": lambda: RK.SHORTCUTS_MESSAGE,
            "sh": lambda: RK.SHORTCUTS_MESSAGE,
        }
        super().__init__(bot, logger)

    def get_commands(self) -> List[str]:
        return ["start", "s", "help", "h", "pomoc"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return []

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        await self._log_system_message(
            logging.INFO,
            get_log_received_start_command(message.from_user.username, message.text),
        )

        if len(content) == 1:
            text = await self.get_response(RK.BASIC_MESSAGE)
            await self.__send_message(message, text)
        elif len(content) == 2:
            command = content[1].lower()
            clean_command = remove_diacritics_and_lowercase(command)
            response_key = self.__RESPONSES.get(clean_command)
            if response_key:
                text = await self.get_response(response_key())
                await self.__send_message(message, text)
            else:
                text = await self.get_response(RK.INVALID_COMMAND_MESSAGE)
                await self.__send_message(message, text)

    async def __send_message(self, message: Message, text: str) -> None:
        await self._answer_markdown(message , text)
        await self._log_system_message(logging.INFO, get_log_start_message_sent(message.from_user.username))
