import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.settings import Settings
from bot.utils.global_dicts import (
    last_clip,
    last_search,
)
from bot.utils.video_manager import VideoManager


class SelectClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['wybierz', 'select', 'w']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/wybierz {message.text}")
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message, "📋 Podaj numer segmentu, który chcesz wybrać. Przykład: /wybierz 1")

        chat_id = message.chat.id
        if chat_id not in last_search:
            return await self.__reply_no_previous_search(message)

        index = int(content[1])
        segments = last_search[chat_id]['segments']

        if index not in range(1, len(segments) + 1):
            return await self.__reply_invalid_segment_number(message, index)

        segment = segments[index - 1]
        video_path = segment['video_path']
        start_time = max(0, segment['start'] - Settings.EXTEND_BEFORE)
        end_time = segment['end'] + Settings.EXTEND_AFTER

        await VideoManager.extract_and_send_clip(chat_id, video_path, start_time, end_time, self._bot)

        last_clip[chat_id] = {'segment': segment, 'type': 'segment'}
        await self._log_system_message(
            logging.INFO,
            f"Segment {segment['id']} selected by user '{message.from_user.username}'.",
        )

    async def __reply_no_previous_search(self, message: Message) -> None:
        await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        await self._log_system_message(logging.INFO, "No previous search results found for user.")

    async def __reply_invalid_segment_number(self, message: Message, segment_number: int) -> None:
        await message.answer("❌ Nieprawidłowy numer segmentu.❌")
        await self._log_system_message(logging.WARNING, f"Invalid segment number provided by user: {segment_number}")
