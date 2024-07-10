import json
import logging
import os
import tempfile
from io import BytesIO
from typing import (
    List,
    Dict,
)

from aiogram.types import (
    Message,
    FSInputFile,
)

from bot.settings import Settings
from bot.main import bot  #fixme czy to importowac ?
from bot_message_handler import BotMessageHandler
from bot.handlers.search_handler import last_search_quotes

from bot.utils.video_handler import VideoManager

last_selected_segment: Dict[int, json] = {}


#fixme całe te funkcje jakieś krzywe ale lece narazie z tym ractorem samym
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


async def compile_clips(selected_segments) -> str:
    temp_files = []
    for segment in selected_segments:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_files.append(temp_file.name)
        video_path = segment['video_path']
        start = max(0, segment['start'] - Settings.EXTEND_BEFORE)
        end = segment['end'] + Settings.EXTEND_AFTER

        await VideoManager(bot).extract_and_send_clip(None, video_path, start, end)

    compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    compiled_output.close()

    await VideoManager(bot).concatenate_clips(temp_files, compiled_output.name)

    file_size_mb = os.path.getsize(compiled_output.name) / (1024 * 1024)
    if file_size_mb > 50:
        raise ValueError(f"Compiled clip exceeds size limit: {file_size_mb:.2f} MB")

    return compiled_output.name


async def send_compiled_clip(chat_id: int, compiled_output: str) -> None:
    with open(compiled_output, 'rb') as f:
        compiled_data = f.read()

    compiled_output_io = BytesIO(compiled_data)
    last_selected_segment[chat_id] = {'compiled_clip': compiled_output_io, 'selected_segments': compiled_data}

    await bot.send_video(chat_id, FSInputFile(compiled_output), supports_streaming=True, width=1920, height=1080)


async def clean_up_temp_files(compiled_output: str) -> None:
    os.remove(compiled_output)


class CompileClipsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['kompiluj', 'compile', 'kom']

    def get_action_name(self) -> str:
        return "compile_handler"

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/kompiluj {message.text}")
        username = message.from_user.username
        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            await self.__reply_no_segments_provided(message)
            return

        if chat_id not in last_search_quotes or not last_search_quotes[chat_id]:
            await self.__reply_no_previous_search_results(message)
            return

        segments = last_search_quotes[chat_id]
        selected_segments, error_message = parse_segments(content[1:], segments)
        if error_message:
            await message.answer(error_message)
            return

        if not selected_segments:
            await self.__reply_no_matching_segments_found(message)
            return

        try:
            compiled_output = await compile_clips(selected_segments)
            await send_compiled_clip(chat_id, compiled_output)
            await clean_up_temp_files(compiled_output)

            await self._log_system_message(logging.INFO, f"Compiled clip sent to user '{username}' and temporary "
                                                         f"files removed.")
        except Exception as e:
            await self.__reply_compilation_error(message, e)

    async def __reply_no_segments_provided(self, message: Message) -> None:
        await message.answer(
            "🔄 Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich "
            "segmentów.",
        )
        await self._log_system_message(logging.INFO, "No segments provided by user.")

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        await self._log_system_message(logging.INFO, "No previous search results found for user.")

    async def __reply_invalid_range(self, message: Message, index: str) -> None:
        await message.answer(f"⚠️ Podano nieprawidłowy zakres segmentów: {index} ⚠️")
        await self._log_system_message(logging.WARNING, f"Invalid range provided by user: {index}")

    async def __reply_invalid_index(self, message: Message, index: str) -> None:
        await message.answer(f"⚠️ Podano nieprawidłowy indeks segmentu: {index} ⚠️")
        await self._log_system_message(logging.WARNING, f"Invalid index provided by user: {index}")

    async def __reply_no_matching_segments_found(self, message: Message) -> None:
        await message.answer("❌ Nie znaleziono pasujących segmentów do kompilacji.❌")
        await self._log_system_message(logging.INFO, "No matching segments found for compilation.")

    async def __reply_compilation_error(self, message: Message, exception: Exception) -> None:
        await message.answer("⚠️ Wystąpił błąd podczas kompilacji klipów.⚠️")
        await self._log_system_message(logging.ERROR, f"An error occurred while compiling clips: {exception}")
