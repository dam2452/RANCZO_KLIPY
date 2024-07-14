import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import (
    get_no_quote_provided_message,
    get_no_segments_found_message,
    get_transcription_response
)
from bot.utils.transcription_search import SearchTranscriptions


class TranscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['transkrypcja', 'trans']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/transkrypcja {message.text}")
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_quote_provided_message())

        quote = ' '.join(content[1:])
        context_size = 15
        result = await SearchTranscriptions.find_segment_with_context(quote, context_size)

        if not result:
            return await self.__reply_no_segments_found(message, quote)

        context_segments = result['context']
        response = get_transcription_response(quote, context_segments)
        await self.__reply_transcription_response(message, response, quote)

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer(get_no_segments_found_message(quote))
        await self._log_system_message(logging.INFO, f"No segments found for quote: '{quote}'")

    async def __reply_transcription_response(self, message: Message, response: str, quote: str) -> None:
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO,
                                       f"Transcription for quote '{quote}' sent to user '{message.from_user.username}'.")
