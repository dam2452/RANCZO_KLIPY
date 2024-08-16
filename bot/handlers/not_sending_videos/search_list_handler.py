import logging
import os
import tempfile
from typing import (
    Dict,
    List,
    Union,
)

from aiogram.types import (
    FSInputFile,
    Message,
)

from bot.database.database_manager import DatabaseManager  # Importujemy DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.search_list_handler_responses import (
    format_search_list_response,
    get_log_no_previous_search_results_message,
    get_log_search_results_sent_message,
    get_no_previous_search_results_message,
)


class SearchListHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['lista', 'list', 'l']

    async def _do_handle(self, message: Message) -> None:
        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)
        if not last_search:
            return await self.__reply_no_previous_search_results(message)

        segments = last_search['segments']
        search_term = last_search['quote']

        response = format_search_list_response(search_term, segments)

        temp_dir = tempfile.gettempdir()
        sanitized_search_term = "".join([c for c in search_term if c.isalpha() or c.isdigit() or c == ' ']).rstrip().replace(" ", "_")
        file_name = os.path.join(temp_dir, f"Ranczo_Klipy_Wyniki_{sanitized_search_term}.txt")
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response)

        input_file = FSInputFile(file_name)
        await self._bot.send_document(message.chat.id, input_file, caption="📄 Znalezione cytaty")
        os.remove(file_name)

        await self._log_system_message(
            logging.INFO,
            get_log_search_results_sent_message(search_term, message.from_user.username),
        )

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await message.answer(get_no_previous_search_results_message())
        await self._log_system_message(logging.INFO, get_log_no_previous_search_results_message(message.chat.id))
