import json
import logging
import os
from typing import (
    Dict,
    List,
)

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.compile_saved_handler import (
    compile_clips,
    send_compiled_clip,
)
from bot.handlers.search_handler import last_search_quotes

last_selected_segment: Dict[int, json] = {}


# fixme całe te funkcje jakieś krzywe ale lece narazie z tym ractorem samym
def parse_segments(content: List[str], segments: List[Dict]) -> (List[Dict], str):
    selected_segments = []

    for index in content:
        if index.lower() == "wszystko":
            return segments, ""

        if '-' in index:
            try:
                start, end = map(int, index.split('-'))
                selected_segments.extend(segments[start - 1:end])
            except ValueError:
                error_message = f"⚠️ Podano nieprawidłowy zakres segmentów: {index} ⚠️"
                return None, error_message
        else:
            try:
                selected_segments.append(segments[int(index) - 1])
            except (ValueError, IndexError):
                error_message = f"⚠️ Podano nieprawidłowy indeks segmentu: {index} ⚠️"
                return None, error_message
    return selected_segments, ""


class CompileClipsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['kompiluj', 'compile', 'kom']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/kompiluj {message.text}")
        username = message.from_user.username
        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            return await self.__reply_no_segments_provided(message)

        if chat_id not in last_search_quotes or not last_search_quotes[chat_id]:
            return await self.__reply_no_previous_search_results(message)

        segments = last_search_quotes[chat_id]
        selected_segments, error_message = parse_segments(content[1:], segments)
        if error_message:
            await message.answer(error_message)
            return

        if not selected_segments:
            return await self.__reply_no_matching_segments_found(message)

        try:
            compiled_output = await compile_clips(selected_segments, self._bot)
            await send_compiled_clip(chat_id, compiled_output, self._bot)
            os.remove(compiled_output)
        except Exception as e:
            return await self.__reply_compilation_error(message, e)

        await self._log_system_message(logging.INFO, f"Compiled clip sent to user '{username}' and temporary files removed.")

    async def __reply_no_segments_provided(self, message: Message) -> None:
        await message.answer("🔄 Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów.")
        await self._log_system_message(logging.INFO, "No segments provided by user.")

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        await self._log_system_message(logging.INFO, "No previous search results found for user.")

    async def __reply_no_matching_segments_found(self, message: Message) -> None:
        await message.answer("❌ Nie znaleziono pasujących segmentów do kompilacji.❌")
        await self._log_system_message(logging.INFO, "No matching segments found for compilation.")

    async def __reply_compilation_error(self, message: Message, exception: Exception) -> None:
        await message.answer("⚠️ Wystąpił błąd podczas kompilacji klipów.⚠️")
        await self._log_system_message(logging.ERROR, f"An error occurred while compiling clips: {exception}")
