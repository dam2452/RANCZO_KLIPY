import logging
import json
from typing import (
    Dict,
    List,
    Union,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.sending_videos.compile_clips_handler_responses import (
    get_compilation_success_message,
    get_invalid_args_count_message,
    get_invalid_index_message,
    get_invalid_range_message,
    get_log_no_matching_segments_found_message,
    get_log_no_previous_search_results_message,
    get_no_matching_segments_found_message,
    get_no_previous_search_results_message,
)
from bot.video.clips_compiler import ClipsCompiler


class CompileClipsHandler(BotMessageHandler):
    class ParseSegmentsException(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def get_commands(self) -> List[str]:
        return ['kompiluj', 'compile', 'kom']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)
        if not last_search or not last_search['segments']:
            return await self.__reply_no_previous_search_results(message)

        # Konwersja JSON na listę segmentów
        segments = json.loads(last_search['segments'])

        selected_segments = self.__parse_segments(content[1:], segments)

        if not selected_segments:
            return await self.__reply_no_matching_segments_found(message)

        # Kompilacja i wysyłanie klipów
        compiled_output = await ClipsCompiler.compile_and_send_clips(message, selected_segments, self._bot, self._logger)
        with open(compiled_output, 'rb') as f:
            compiled_clip_data = f.read()
        # Zapis skompilowanego klipu do bazy danych
        await DatabaseManager.insert_last_clip(
            chat_id=message.chat.id,
            segment=None,
            compiled_clip=compiled_clip_data,  # Przekazujemy dane binarne, a nie ścieżkę
            clip_type='compiled'
        )

        await self._log_system_message(logging.INFO, get_compilation_success_message(message.from_user.username))

    @staticmethod
    def __parse_segments(content: List[str], segments: List[Dict[str, Union[str, float]]]) -> List[Dict[str, Union[str, float]]]:
        selected_segments = []
        for index in content:
            if index.lower() == "wszystko":
                selected_segments.extend(
                    {'video_path': segment['video_path'], 'start': segment['start'], 'end': segment['end']}
                    for segment in segments
                )
                return selected_segments

            if '-' in index:
                selected_segments.extend(CompileClipsHandler.__parse_range(index, segments))
            else:
                try:
                    selected_segments.append(CompileClipsHandler.__parse_single(index, segments))
                except CompileClipsHandler.ParseSegmentsException:
                    continue

        return selected_segments

    @staticmethod
    def __parse_range(index: str, segments: List[Dict[str, Union[str, float]]]) -> List[Dict[str, Union[str, float]]]:
        try:
            start, end = [int(i) for i in index.split('-')]
            return [
                {'video_path': segments[i - 1]['video_path'], 'start': segments[i - 1]['start'], 'end': segments[i - 1]['end']}
                for i in range(start, end + 1)
            ]
        except ValueError as e:
            raise CompileClipsHandler.ParseSegmentsException(get_invalid_range_message(index)) from e

    @staticmethod
    def __parse_single(index: str, segments: List[Dict[str, Union[str, float]]]) -> Dict[str, Union[str, float]]:
        try:
            segment = segments[int(index) - 1]
            return {'video_path': segment['video_path'], 'start': segment['start'], 'end': segment['end']}
        except (ValueError, IndexError) as e:
            raise CompileClipsHandler.ParseSegmentsException(get_invalid_index_message(index)) from e

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await message.answer(get_no_previous_search_results_message())
        await self._log_system_message(logging.INFO, get_log_no_previous_search_results_message())

    async def __reply_no_matching_segments_found(self, message: Message) -> None:
        await message.answer(get_no_matching_segments_found_message())
        await self._log_system_message(logging.INFO, get_log_no_matching_segments_found_message())
