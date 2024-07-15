import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.bot_message_handler_responses import (
    get_log_no_segments_found_message,
    get_no_segments_found_message,
)
from bot.handlers.responses.search_handler_responses import (
    format_search_response,
    get_invalid_args_count_message,
    get_log_search_results_sent_message,
)
from bot.utils.global_dicts import last_search
from bot.utils.transcription_search import SearchTranscriptions


class SearchHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['szukaj', 'search', 'sz']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        quote = ' '.join(content[1:])

        segments = await SearchTranscriptions.find_segment_by_quote(quote, return_all=True)
        if not segments:
            return await self.__reply_no_segments_found(message, quote)

        last_search[message.chat.id] = {'quote': quote, 'segments': segments}

        response = format_search_response(len(segments), segments)

        await self.__send_search_results(message, response, quote)

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer(get_no_segments_found_message(quote))
        await self._log_system_message(logging.INFO, get_log_no_segments_found_message(quote))

    async def __send_search_results(self, message: Message, response: str, quote: str) -> None:
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, get_log_search_results_sent_message(quote, message.from_user.username))
