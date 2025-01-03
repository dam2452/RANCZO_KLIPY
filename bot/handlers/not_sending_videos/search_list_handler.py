import json
import logging
from pathlib import Path
import tempfile
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.not_sending_videos.search_list_handler_responses import (
    format_search_list_response,
    get_log_no_previous_search_results_message,
    get_log_search_results_sent_message,
)
from bot.database.response_keys import ResponseKey as RK

class SearchListHandler(BotMessageHandler):

    FILE_NAME_TEMPLATE = "RanczoKlipy_Lista_{sanitized_search_term}.txt"

    def get_commands(self) -> List[str]:
        return ["lista", "list", "l"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_last_search_exists,
        ]

    async def __check_last_search_exists(self, message: Message) -> bool:
        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)
        if not last_search:
            await self.__reply_no_previous_search_results(message)
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)

        try:
            segments = json.loads(last_search.segments)
        except (json.JSONDecodeError, TypeError):
            return await self.__reply_no_previous_search_results(message)

        search_term = last_search.quote
        if not segments or not search_term:
            return await self.__reply_no_previous_search_results(message)

        response = format_search_list_response(search_term, segments)
        temp_dir = Path(tempfile.gettempdir())

        sanitized_search_term = self.__sanitize_search_term(search_term)

        file_path = temp_dir / self.FILE_NAME_TEMPLATE.format(sanitized_search_term=sanitized_search_term)

        with file_path.open("w", encoding="utf-8") as file:
            file.write(response)

        await self._answer_document(message, file_path, caption="📄 Wszystkie znalezione cytaty 📄")
        file_path.unlink()

        await self._log_system_message(
            logging.INFO,
            get_log_search_results_sent_message(search_term, message.from_user.username),
        )

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await self._answer(message,await self.get_response(RK.NO_PREVIOUS_SEARCH_RESULTS))
        await self._log_system_message(logging.INFO, get_log_no_previous_search_results_message(message.chat.id))

    @staticmethod
    def __sanitize_search_term(search_term: str) -> str:
        allowed_characters = [c.isalpha() or c.isdigit() or c == " " for c in search_term]
        filtered_chars = [c for c, allowed in zip(search_term, allowed_characters) if allowed]
        filtered_string = "".join(filtered_chars)
        stripped_string = filtered_string.rstrip()
        sanitized_string = stripped_string.replace(" ", "_")
        return sanitized_string
