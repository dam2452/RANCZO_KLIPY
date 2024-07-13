import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.settings import Settings
from bot.utils.global_dicts import last_selected_segment
from bot.utils.transcription_search import SearchTranscriptions
from bot.utils.video_manager import (
    FFmpegException,
    VideoManager,
)


class ClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['klip', 'clip', 'k']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/klip {message.text}")
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, "🔎 Podaj cytat, który chcesz znaleźć. Przykład: /klip Nie szkoda panu tego pięknego gabinetu?")

        quote = ' '.join(content[1:])

        search_transcriptions = SearchTranscriptions()
        segments = await search_transcriptions.find_segment_by_quote(quote, return_all=False)

        if not segments:
            return await self.__reply_no_segments_found(message, quote)

        segment = segments[0] if isinstance(segments, list) else segments
        video_path = segment['video_path']
        start_time = max(0, segment['start'] - Settings.EXTEND_BEFORE)
        end_time = segment['end'] + Settings.EXTEND_AFTER

        try:
            await VideoManager.extract_and_send_clip(message.chat.id, video_path, start_time, end_time, self._bot)
        except FFmpegException as e:
            return await self.__reply_extraction_failure(message, e)

        last_selected_segment[message.chat.id] = segment
        await self.__log_segment_and_clip_success(message.chat.id, message.from_user.username)

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer("❌ Nie znaleziono pasujących cytatów.❌")
        await self._log_system_message(logging.INFO, f"No segments found for quote: '{quote}'")

    async def __reply_extraction_failure(self, message: Message, exception: FFmpegException) -> None:
        await message.answer(f"⚠️ Nie udało się wyodrębnić klipu wideo: {exception}")
        await self._log_system_message(logging.ERROR, f"Failed to extract video clip: {exception}")

    async def __log_segment_and_clip_success(self, chat_id: int, username: str) -> None:
        await self._log_system_message(logging.INFO, f"Segment saved as last selected for chat ID '{chat_id}'")
        await self._log_system_message(logging.INFO, f"Video clip extracted successfully for user '{username}'.")
