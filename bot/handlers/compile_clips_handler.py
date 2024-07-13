import logging
import os
from typing import (
    Dict,
    List,
    Union,
)

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.functions import (
    compile_clips,
    send_compiled_clip,
)
from bot.utils.global_dicts import (
    last_search,
    last_clip,
)


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
            return await self._reply_invalid_args_count(
                message,
                "🔄 Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów."
            )

        if chat_id not in last_search or not last_search[chat_id]['segments']:
            return await self.__reply_no_previous_search_results(message)

        segments = last_search[chat_id]['segments']
        selected_segments: List[bytes] = self.__parse_segments(content[1:], segments)

        if not selected_segments:
            return await self.__reply_no_matching_segments_found(message)

        compiled_output: str = await compile_clips(selected_segments)
        await send_compiled_clip(chat_id, compiled_output, self._bot)
        if os.path.exists(compiled_output):
            os.remove(compiled_output)

        last_clip[chat_id] = {'compiled_clip': compiled_output, 'type': 'compiled'}
        await self._log_system_message(logging.INFO, f"Compiled clip sent to user '{username}' and temporary files removed.")

    @staticmethod
    def __parse_segments(content: List[str], segments: List[Dict[str, Union[str, bytes]]]) -> List[bytes]:
        selected_segments = []

        for index in content:
            if index.lower() == "wszystko":
                selected_segments.extend(segment['data'] for segment in segments)
                return selected_segments

            if '-' in index:
                selected_segments.extend(CompileClipsHandler.__parse_range(index, segments))
            else:
                selected_segments.append(CompileClipsHandler.__parse_single(index, segments))

        return selected_segments

    @staticmethod
    def __parse_range(index: str, segments: List[Dict[str, Union[str, bytes]]]) -> List[bytes]:
        try:
            start, end = map(int, index.split('-'))
            return [segments[i - 1]['data'] for i in range(start, end + 1)]
        except ValueError:
            raise CompileClipsHandler.ParseSegmentsException(f"⚠️ Podano nieprawidłowy zakres segmentów: {index} ⚠️")

    @staticmethod
    def __parse_single(index: str, segments: List[Dict[str, Union[str, bytes]]]) -> bytes:
        try:
            return segments[int(index) - 1]['data']
        except (ValueError, IndexError):
            raise CompileClipsHandler.ParseSegmentsException(f"⚠️ Podano nieprawidłowy indeks segmentu: {index} ⚠️")

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        await self._log_system_message(logging.INFO, "No previous search results found for user.")

    async def __reply_no_matching_segments_found(self, message: Message) -> None:
        await message.answer("❌ Nie znaleziono pasujących segmentów do kompilacji.❌")
        await self._log_system_message(logging.INFO, "No matching segments found for compilation.")
