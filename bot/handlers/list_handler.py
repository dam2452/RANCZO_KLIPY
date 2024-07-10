import logging
import os
import tempfile
from typing import List

from aiogram.types import (
    Message,
    FSInputFile,
)

from tabulate import tabulate

from bot_message_handler import BotMessageHandler
from bot.handlers.search_handler import (
    last_search_quotes,
    last_search_terms,
)


class SearchListHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['lista', 'list', 'l']

    def get_action_name(self) -> str:
        return "list_handler"

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/lista {message.text}")
        username = message.from_user.username
        chat_id = message.chat.id

        if chat_id not in last_search_quotes or chat_id not in last_search_terms:
            await self.__reply_no_previous_search_results(message, chat_id)
            return

        segments = last_search_quotes[chat_id]
        search_term = last_search_terms[chat_id]

        response = f"🔍 Znaleziono {len(segments)} pasujących segmentów dla zapytania '{search_term}':\n"
        segment_lines = []

        for i, segment in enumerate(segments, start=1):
            episode_info = segment.get('episode_info', {})
            total_episode_number = episode_info.get('episode_number', 'Unknown')
            season_number = (total_episode_number - 1) // 13 + 1 if isinstance(total_episode_number, int) else 'Unknown'
            episode_number_in_season = (total_episode_number - 1) % 13 + 1 if isinstance(total_episode_number,
                                                                                         int) else 'Unknown'

            season = str(season_number).zfill(2)
            episode_number = str(episode_number_in_season).zfill(2)
            episode_title = episode_info.get('title', 'Unknown')
            start_time = int(segment['start'])
            minutes, seconds = divmod(start_time, 60)
            time_formatted = f"{minutes:02}:{seconds:02}"

            episode_formatted = f"S{season}E{episode_number}"
            line = [i, episode_formatted, episode_title, time_formatted]
            segment_lines.append(line)

        table = tabulate(
            segment_lines, headers=["#", "Odcinek", "Tytuł", "Czas"], tablefmt="pipe",
            colalign=("left", "center", "left", "right"),
        )
        response += f"{table}\n"

        temp_dir = tempfile.gettempdir()
        sanitized_search_term = "".join(
            [c for c in search_term if c.isalpha() or c.isdigit() or c == ' ']).rstrip().replace(" ", "_")
        file_name = os.path.join(temp_dir, f"Ranczo_Klipy_Wyniki_{sanitized_search_term}.txt")
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response)

        input_file = FSInputFile(file_name)
        await self._bot.send_document(chat_id, input_file, caption="📄 Znalezione cytaty")
        os.remove(file_name)

        await self._log_system_message(logging.INFO,
                                       f"List of search results for term '{search_term}' sent to user {username}.")

    async def __reply_unauthorized_access(self, message: Message, username: str) -> None:
        await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.❌")
        await self._log_system_message(logging.WARNING, f"Unauthorized access attempt by user: {username}")

    async def __reply_no_previous_search_results(self, message: Message, chat_id: int) -> None:
        await message.answer("🔍 Nie znaleziono wcześniejszych wyników wyszukiwania.")
        await self._log_system_message(logging.INFO, f"No previous search results found for chat ID {chat_id}.")

