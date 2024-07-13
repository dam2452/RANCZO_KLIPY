import logging
import os
from typing import (
    Dict,
    List,
    Union,
)

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.functions import (
    compile_clips,
    send_compiled_clip,
)
from bot.utils.global_dicts import last_search_quotes


class CompileClipsHandler(BotMessageHandler):
    class ParseSegmentsException(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def get_commands(self) -> List[str]:
        return ['kompiluj', 'compile', 'kom']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/kompiluj {message.text}")
        username = message.from_user.username
        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message,
                                                        "🔄 Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów.")

        if chat_id not in last_search_quotes or not last_search_quotes[chat_id]:
            return await self.__reply_no_previous_search_results(message)

        segments = last_search_quotes[chat_id]
        try:
            selected_segments: List[bytes] = self.__parse_segments(content[1:], segments)
        except self.ParseSegmentsException as e:
            await message.answer(e.message)
            return

        if not selected_segments:
            return await self.__reply_no_matching_segments_found(message)

        try:
            compiled_output: str = await compile_clips(selected_segments)
            await send_compiled_clip(chat_id, compiled_output, self._bot)
            os.remove(compiled_output)
        except Exception as e:
            return await self.__reply_compilation_error(message, e)

        await self._log_system_message(logging.INFO, f"Compiled clip sent to user '{username}' and temporary files "
                                                     f"removed.")

    @staticmethod
    def __parse_segments(content: List[str], segments: List[Dict[str, Union[str, bytes]]]) -> List[bytes]:
        selected_segments = []

        for index in content:
            if index.lower() == "wszystko":
                selected_segments.extend(segment['data'] for segment in segments)
                return selected_segments

            if '-' in index:
                try:
                    start, end = map(int, index.split('-'))
                    selected_segments.extend(segments[i - 1]['data'] for i in range(start, end + 1))
                except ValueError as e:
                    raise CompileClipsHandler.ParseSegmentsException(
                        f"⚠️ Podano nieprawidłowy zakres segmentów: {index} ⚠️") from e
            else:
                try:
                    selected_segments.append(segments[int(index) - 1]['data'])
                except (ValueError, IndexError) as e:
                    raise CompileClipsHandler.ParseSegmentsException(
                        f"⚠️ Podano nieprawidłowy indeks segmentu: {index} ⚠️") from e

        return selected_segments

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        await self._log_system_message(logging.INFO, "No previous search results found for user.")

    async def __reply_no_matching_segments_found(self, message: Message) -> None:
        await message.answer("❌ Nie znaleziono pasujących segmentów do kompilacji.❌")
        await self._log_system_message(logging.INFO, "No matching segments found for compilation.")

    async def __reply_compilation_error(self, message: Message, exception: Exception) -> None:
        await message.answer("⚠️ Wystąpił błąd podczas kompilacji klipów.⚠️")
        await self._log_system_message(logging.ERROR, f"An error occurred while compiling clips: {exception}")
