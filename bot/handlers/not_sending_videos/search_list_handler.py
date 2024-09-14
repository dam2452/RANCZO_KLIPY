import json
import logging
import os
import tempfile
from typing import List

from aiogram.types import (
    FSInputFile,
    Message,
)

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.search_list_handler_responses import (
    format_search_list_response,
    get_log_no_previous_search_results_message,
    get_log_search_results_sent_message,
    get_no_previous_search_results_message,
)

FILE_NAME_TEMPLATE = "RanczoKlipy_Lista_{sanitized_search_term}.txt"

class SearchListHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["lista", "list", "l"]

    async def _do_handle(self, message: Message) -> None:
        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)

        if not last_search:
            return await self.__reply_no_previous_search_results(message)

        try:
            segments = json.loads(last_search.segments)
        except (json.JSONDecodeError, TypeError):
            return await self.__reply_no_previous_search_results(message)

        search_term = last_search.quote
        if not segments or not search_term:
            return await self.__reply_no_previous_search_results(message)

        response = format_search_list_response(search_term, segments)
        temp_dir = tempfile.gettempdir()

        sanitized_search_term = self.__sanitize_search_term(search_term)

        file_name = os.path.join(temp_dir, FILE_NAME_TEMPLATE.format(sanitized_search_term=sanitized_search_term))

        with open(file_name, "w", encoding="utf-8") as file:
            file.write(response)

        input_file = FSInputFile(file_name)
        await self._bot.send_document(message.chat.id, input_file, caption="📄 Wszystkie znalezione cytaty 📄")
        os.remove(file_name)

        await self._log_system_message(
            logging.INFO,
            get_log_search_results_sent_message(search_term, message.from_user.username),
        )

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await message.answer(get_no_previous_search_results_message())
        await self._log_system_message(logging.INFO, get_log_no_previous_search_results_message(message.chat.id))

    @staticmethod
    def __sanitize_search_term(search_term: str) -> str:
        return "".join([c for c in search_term if c.isalpha() or c.isdigit() or c == " "]).rstrip().replace(" ", "_")
