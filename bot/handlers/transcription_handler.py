import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.bot_message_handler_responses import (
    get_log_no_segments_found_message,
    get_no_segments_found_message,
)
from bot.handlers.responses.transcription_handler_responses import (
    get_log_transcription_response_sent_message,
    get_no_quote_provided_message,
    get_transcription_response,
)
from bot.utils.transcription_finder import TranscriptionFinder


class TranscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['transkrypcja', 'trans']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_quote_provided_message())

        quote = ' '.join(content[1:])
        result = await TranscriptionFinder.find_segment_with_context(quote, context_size=15)

        if not result:
            return await self.__reply_no_segments_found(message, quote)

        context_segments = result['context']
        response = get_transcription_response(quote, context_segments)
        await self.__reply_transcription_response(message, response, quote)

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer(get_no_segments_found_message(quote))
        await self._log_system_message(logging.INFO, get_log_no_segments_found_message(quote))

    async def __reply_transcription_response(self, message: Message, response: str, quote: str) -> None:
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, get_log_transcription_response_sent_message(quote, message.from_user.username))
