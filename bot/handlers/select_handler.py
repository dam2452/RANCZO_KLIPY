import json
import logging
from typing import (
    Dict,
    List,
)

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.settings import Settings
from bot.utils.video_handler import VideoManager

last_search_quotes: Dict[int, List[json]] = {} #fixme to jest powtórzone setny raz ale czeka na zrobienie bazy
last_selected_segment: Dict[int, json] = {}


class SelectClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['wybierz', 'select', 'w']

    def get_action_name(self) -> str:
        return "select_handler"

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/wybierz {message.text}")
        content = message.text.split()

        if len(content) < 2:
            return await self.__reply_no_segment_provided(message)

        chat_id = message.chat.id
        if chat_id not in last_search_quotes:
            return await self.__reply_no_previous_search(message)

        index = int(content[1]) - 1
        segments = last_search_quotes[chat_id]

        if index < 0 or index >= len(segments):
            return await self.__reply_invalid_segment_number(message, index + 1)

        segment = segments[index]
        video_path = segment['video_path']
        start_time = max(0, segment['start'] - Settings.EXTEND_BEFORE)
        end_time = segment['end'] + Settings.EXTEND_AFTER

        video_manager = VideoManager(self._bot)
        await video_manager.extract_and_send_clip(chat_id, video_path, start_time, end_time)

        last_selected_segment[chat_id] = segment
        await self._log_system_message(
            logging.INFO,
            f"Segment {segment['id']} selected by user '{message.from_user.username}'.",
        )

    async def __reply_no_segment_provided(self, message: Message) -> None:
        await message.answer("📋 Podaj numer segmentu, który chcesz wybrać. Przykład: /wybierz 1")
        await self._log_system_message(logging.INFO, "No segment number provided by user.")

    async def __reply_no_previous_search(self, message: Message) -> None:
        await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        await self._log_system_message(logging.INFO, "No previous search results found for user.")

    async def __reply_invalid_segment_number(self, message: Message, segment_number: int) -> None:
        await message.answer("❌ Nieprawidłowy numer segmentu.❌")
        await self._log_system_message(logging.WARNING, f"Invalid segment number provided by user: {segment_number}")
