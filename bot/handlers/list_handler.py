import logging
import os
import tempfile
from typing import List

from aiogram.types import (
    FSInputFile,
    Message,
)
from tabulate import tabulate

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.functions import format_segment
from bot.utils.global_dicts import (
    last_search_quotes,
    last_search_terms,
)


class SearchListHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['lista', 'list', 'l']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/lista {message.text}")
        username = message.from_user.username
        chat_id = message.chat.id

        if chat_id not in last_search_quotes or chat_id not in last_search_terms:
            return await self.__reply_no_previous_search_results(message, chat_id)

        segments = last_search_quotes[chat_id]
        search_term = last_search_terms[chat_id]

        response = f"🔍 Znaleziono {len(segments)} pasujących segmentów dla zapytania '{search_term}':\n"
        segment_lines = []

        for i, segment in enumerate(segments, start=1):
            segment_info = format_segment(segment)
            segment_lines.append([i, segment_info.episode_formatted, segment_info.episode_title, segment_info.time_formatted])

        table = tabulate(
            segment_lines, headers=["#", "Odcinek", "Tytuł", "Czas"], tablefmt="pipe", colalign=("left", "center", "left", "right"),
        )
        response += f"{table}\n"

        temp_dir = tempfile.gettempdir()
        sanitized_search_term = "".join([c for c in search_term if c.isalpha() or c.isdigit() or c == ' ']).rstrip().replace(" ", "_")
        file_name = os.path.join(temp_dir, f"Ranczo_Klipy_Wyniki_{sanitized_search_term}.txt")
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response)

        input_file = FSInputFile(file_name)
        await self._bot.send_document(chat_id, input_file, caption="📄 Znalezione cytaty")
        os.remove(file_name)

        await self._log_system_message(
            logging.INFO,
            f"List of search results for term '{search_term}' sent to user {username}.",
        )

    async def __reply_no_previous_search_results(self, message: Message, chat_id: int) -> None:
        await message.answer("🔍 Nie znaleziono wcześniejszych wyników wyszukiwania.")
        await self._log_system_message(logging.INFO, f"No previous search results found for chat ID {chat_id}.")
