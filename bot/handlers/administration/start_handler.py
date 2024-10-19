import logging
from typing import (
    Callable,
    Dict,
    List,
)

from aiogram import Bot
from aiogram.types import Message

from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.start_handler_responses import (
    get_all_message,
    get_basic_message,
    get_edit_message,
    get_invalid_command_message,
    get_list_message,
    get_log_received_start_command,
    get_log_start_message_sent,
    get_menagement_message,
    get_reporting_message,
    get_search_message,
    get_shortcuts_message,
    get_subscriptions_message,
)
from bot.utils.functions import remove_diacritics_and_lowercase


class StartHandler(BotMessageHandler):
    def __init__(self, bot: Bot, logger: logging.Logger):
        self.__RESPONSES: Dict[str, Callable[[], str]] = {
            "lista": get_list_message,
            "list": get_list_message,
            "l": get_list_message,

            "wszystko": get_all_message,
            "all": get_all_message,
            "a": get_all_message,

            "wyszukiwanie": get_search_message,
            "search": get_search_message,
            "s": get_search_message,

            "edycja": get_edit_message,
            "edit": get_edit_message,
            "e": get_edit_message,

            "zarzadzanie": get_menagement_message,
            "management": get_menagement_message,
            "m": get_menagement_message,

            "raportowanie": get_reporting_message,
            "reporting": get_reporting_message,
            "r": get_reporting_message,

            "subskrypcje": get_subscriptions_message,
            "subscriptions": get_subscriptions_message,
            "sub": get_subscriptions_message,

            "skroty": get_shortcuts_message,
            "shortcuts": get_shortcuts_message,
            "sh": get_shortcuts_message,
        }
        super().__init__(bot, logger)

    def get_commands(self) -> List[str]:
        return ["start", "s", "help", "h", "pomoc"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return []

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        await self._log_system_message(logging.INFO, get_log_received_start_command(message.from_user.username, message.text))

        if len(content) == 1:
            await self.__send_message(message, get_basic_message())
        elif len(content) == 2:
            command = content[1].lower()
            clean_command = remove_diacritics_and_lowercase(command)
            response_func = self.__RESPONSES.get(clean_command)
            if response_func:
                await self.__send_message(message, response_func())
            else:
                await self.__send_message(message, get_invalid_command_message())

    async def __send_message(self, message: Message, text: str) -> None:
        await self._answer_markdown(message , text)
        await self._log_system_message(logging.INFO, get_log_start_message_sent(message.from_user.username))
