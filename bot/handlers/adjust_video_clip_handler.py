import logging
import os
import tempfile
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers_old.clip_search import last_search_quotes
from bot.handlers_old.handle_clip import last_selected_segment
from bot.settings import Settings
from bot.utils.video_handler import (
    FFmpegException,
    VideoManager,
    VideoProcessor,
)


class AdjustVideoClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['dostosuj', 'adjust', 'd']

    def get_action_name(self) -> str:
        return "adjust_video_clip"

    async def _do_handle(self, message: Message) -> None:
        chat_id = message.chat.id
        content = message.text.split()

        if len(content) == 4:
            index = int(content[1]) - 1
            before_adjustment = float(content[2])
            after_adjustment = float(content[3])
            if chat_id not in last_search_quotes:
                await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
                await self._log_system_message(logging.INFO, "No previous search results found for user.")
                return
            segments = last_search_quotes[chat_id]
            segment_info = segments[index]
        elif len(content) == 3:
            before_adjustment = float(content[1])
            after_adjustment = float(content[2])
            if chat_id not in last_selected_segment:
                await message.answer("⚠️ Najpierw wybierz cytat za pomocą /klip.⚠️")
                await self._log_system_message(logging.INFO, "No segment selected by user.")
                return
            segment_info = last_selected_segment[chat_id]
        else:
            await message.answer(
                "📝 Podaj czas w formacie `<float> <float>` lub `<index> <float> <float>`. Przykład: /dostosuj 10.5 -15.2 lub /dostosuj 1 10.5 -15.2",
            )
            await self._log_system_message(logging.INFO, "Invalid number of arguments provided by user.")
            return

        await self._log_system_message(logging.INFO, f"Segment Info: {segment_info}")

        original_start_time = segment_info['start'] - Settings.EXTEND_BEFORE
        original_end_time = segment_info['end'] + Settings.EXTEND_AFTER

        start_time = original_start_time - before_adjustment
        end_time = original_end_time + after_adjustment

        start_time = max(0, start_time)
        if end_time <= start_time:
            await message.answer("⚠️ Czas zakończenia musi być późniejszy niż czas rozpoczęcia.⚠️")
            await self._log_system_message(logging.INFO, "End time must be later than start time.")
            return

        clip_path = segment_info['video_path']
        output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

        try:
            await VideoProcessor.extract_clip(clip_path, start_time, end_time, output_filename)
        except FFmpegException as e:
            await message.answer(f"⚠️ Nie udało się zmienić klipu wideo: {str(e)}")
            await self._log_system_message(logging.ERROR, f"Failed to adjust video clip: {e}")

        file_size_mb = os.path.getsize(output_filename) / (1024 * 1024)
        await self._log_system_message(logging.INFO, f"Clip size: {file_size_mb:.2f} MB")

        if file_size_mb > self.MAX_TELEGRAM_FILE_SIZE_MB:
            await message.answer(
                f"❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to {self.MAX_TELEGRAM_FILE_SIZE_MB} MB.❌",
            )
            await self._log_system_message(logging.WARNING, f"Clip size {file_size_mb:.2f} MB exceeds the {self.MAX_TELEGRAM_FILE_SIZE_MB} MB limit.")
        else:
            await VideoManager(self._bot).send_video(chat_id, output_filename)

        os.remove(output_filename)
        await self._log_system_message(logging.INFO, f"Temporary file '{output_filename}' removed after sending clip.")

        segment_info['start'] = start_time
        segment_info['end'] = end_time
        last_selected_segment[chat_id] = segment_info
        await self._log_system_message(logging.INFO, f"Updated segment info for chat ID '{chat_id}'")
        await self._log_system_message(logging.INFO, f"Video clip adjusted successfully for user '{message.from_user.username}'.")

