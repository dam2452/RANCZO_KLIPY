import logging
from typing import (
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
from bot.responses.not_sending_videos.episode_list_handler_responses import get_invalid_argument_count_log_message
from bot.utils.functions import remove_diacritics_and_lowercase


class StartHandler(BotMessageHandler):
    def __init__(self, bot: Bot, logger: logging.Logger):
        self.__RESPONSES: Dict[str, str] = {
            "lista": RK.LIST_MESSAGE,
            "list": RK.LIST_MESSAGE,
            "l": RK.LIST_MESSAGE,

            "wszystko": RK.ALL_MESSAGE,
            "all": RK.ALL_MESSAGE,
            "a": RK.ALL_MESSAGE,

            "wyszukiwanie": RK.SEARCH_MESSAGE,
            "search": RK.SEARCH_MESSAGE,
            "s": RK.SEARCH_MESSAGE,

            "edycja": RK.EDIT_MESSAGE,
            "edit": RK.EDIT_MESSAGE,
            "e": RK.EDIT_MESSAGE,

            "zarzadzanie": RK.MANAGEMENT_MESSAGE,
            "management": RK.MANAGEMENT_MESSAGE,
            "m": RK.MANAGEMENT_MESSAGE,

            "raportowanie": RK.REPORTING_MESSAGE,
            "reporting": RK.REPORTING_MESSAGE,
            "r": RK.REPORTING_MESSAGE,

            "subskrypcje": RK.SUBSCRIPTIONS_MESSAGE,
            "subscriptions": RK.SUBSCRIPTIONS_MESSAGE,
            "sub": RK.SUBSCRIPTIONS_MESSAGE,

            "skroty": RK.SHORTCUTS_MESSAGE,
            "shortcuts": RK.SHORTCUTS_MESSAGE,
            "sh": RK.SHORTCUTS_MESSAGE,
        }
        super().__init__(bot, logger)

    def get_commands(self) -> List[str]:
        return ["start", "s", "help", "h", "pomoc"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [self._validate_specific_argument_count]

    async def _validate_specific_argument_count(self, message: Message) -> bool:
        if not await self._validate_argument_count(message, 1, await self.get_response(RK.INVALID_COMMAND_MESSAGE)):
            return False

        content = message.text.split()
        if len(content) not in {1, 2}:
            text = await self.get_response(RK.INVALID_COMMAND_MESSAGE)
            await self._answer_markdown(message, text)
            await self._log_system_message(
                logging.WARNING,
                get_invalid_argument_count_log_message(message.from_user.id, message.text),
            )
            return False

        return True

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
                text = await self.get_response(response_key)
                await self.__send_message(message, text)
            else:
                text = await self.get_response(RK.INVALID_COMMAND_MESSAGE)
                await self.__send_message(message, text)

    async def __send_message(self, message: Message, text: str) -> None:
        await self._answer_markdown(message, text)
        await self._log_system_message(logging.INFO, get_log_start_message_sent(message.from_user.username))
