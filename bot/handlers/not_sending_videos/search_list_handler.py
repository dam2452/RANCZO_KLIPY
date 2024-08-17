import json
import logging
import os
import tempfile
from typing import List

from aiogram.types import (
    FSInputFile,
    Message,
)
import asyncpg

from bot.database.database_manager import DatabaseManager
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

        if isinstance(last_search, asyncpg.Record):
            last_search = dict(last_search)
            logging.info(f"Converted last_search to dictionary for chat_id: {message.chat.id}")

        if isinstance(last_search, dict):
            logging.info(f"last_search is already a dictionary for chat_id: {message.chat.id}")
        elif isinstance(last_search, str):
            try:
                logging.info(f"Attempting to decode last_search JSON for chat_id: {message.chat.id}")
                last_search = json.loads(last_search)
                logging.info(f"Decoded last_search: {last_search}")
            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode last_search JSON for chat_id: {message.chat.id}. Error: {str(e)}")
                return await self.__reply_no_previous_search_results(message)
        else:
            logging.error(f"Unexpected type for last_search: {type(last_search)} for chat_id: {message.chat.id}")
            return await self.__reply_no_previous_search_results(message)

        if not isinstance(last_search, dict):
            logging.error(f"Expected a dictionary for last_search but got {type(last_search)} for chat_id: {message.chat.id}")
            return await self.__reply_no_previous_search_results(message)

        segments = last_search.get('segments')
        if isinstance(segments, str):
            try:
                logging.info(f"Attempting to decode segments JSON for chat_id: {message.chat.id}")
                segments = json.loads(segments)
                logging.info(f"Decoded segments: {segments}")
                last_search['segments'] = segments
            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode segments JSON for chat_id: {message.chat.id}. Error: {str(e)}")
                return await self.__reply_no_previous_search_results(message)

        search_term = last_search.get('quote')

        if not segments or not search_term:
            logging.warning(f"No segments or search_term found in last_search for chat_id: {message.chat.id}")
            return await self.__reply_no_previous_search_results(message)

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
