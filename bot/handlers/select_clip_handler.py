import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.handlers.responses.bot_message_handler_responses import (
    get_extraction_failure_message,
    get_log_extraction_failure_message,
)
from bot.handlers.responses.select_clip_handler_responses import (
    get_invalid_args_count_message,
    get_invalid_segment_number_message,
    get_log_invalid_segment_number_message,
    get_log_no_previous_search_message,
    get_log_segment_selected_message,
    get_no_previous_search_message,
)
from bot.utils.functions import extract_and_send_clip
from bot.utils.global_dicts import (
    last_clip,
    last_search,
)
from bot.utils.video_utils import FFmpegException


class SelectClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['wybierz', 'select', 'w']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        if message.chat.id not in last_search:
            return await self.__reply_no_previous_search(message)

        index = int(content[1])
        segments = last_search[message.chat.id]['segments']

        if index not in range(1, len(segments) + 1):
            return await self.__reply_invalid_segment_number(message, index)

        segment = segments[index - 1]
        try:
            await extract_and_send_clip(segments[index - 1], message, self._bot)
        except FFmpegException as e:
            return await self.__reply_extraction_failure(message, e)

        last_clip[message.chat.id] = {'segment': segment, 'type': 'segment'}
        await self._log_system_message(logging.INFO, get_log_segment_selected_message(segment['id'], message.from_user.username))

    async def __reply_no_previous_search(self, message: Message) -> None:
        await message.answer(get_no_previous_search_message())
        await self._log_system_message(logging.INFO, get_log_no_previous_search_message())

    async def __reply_extraction_failure(self, message: Message, exception: FFmpegException) -> None:
        await message.answer(get_extraction_failure_message())
        await self._log_system_message(logging.ERROR, get_log_extraction_failure_message(exception))

    async def __reply_invalid_segment_number(self, message: Message, segment_number: int) -> None:
        await message.answer(get_invalid_segment_number_message())
        await self._log_system_message(logging.WARNING, get_log_invalid_segment_number_message(segment_number))
