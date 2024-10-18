import json
import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.bot_message_handler_responses import (
    get_log_no_segments_found_message,
    get_message_too_long_message,
    get_no_segments_found_message,
)
from bot.responses.not_sending_videos.search_handler_responses import (
    format_search_response,
    get_invalid_args_count_message,
    get_log_search_results_sent_message,
)
from bot.search.transcription_finder import TranscriptionFinder
from bot.settings import settings
from bot.utils.functions import validate_argument_count


class SearchHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["szukaj", "search", "sz"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self._validate_argument_count,
            self._validate_quote_length,
        ]

    async def _validate_argument_count(self, message: Message) -> bool:
        return await validate_argument_count(
            message, 2, self._reply_invalid_args_count,
            get_invalid_args_count_message(),
        )

    @staticmethod
    async def _validate_quote_length(message: Message) -> bool:
        quote = " ".join(message.text.split()[1:])
        if not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and len(quote) > settings.MAX_SEARCH_QUERY_LENGTH:
            await message.answer(get_message_too_long_message())
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        quote = " ".join(message.text.split()[1:])

        segments = await TranscriptionFinder.find_segment_by_quote(quote, self._logger, return_all=True)
        if not segments:
            return await self.__reply_no_segments_found(message, quote)

        segments_json = json.dumps(segments)

        await DatabaseManager.insert_last_search(
            chat_id=message.chat.id,
            quote=quote,
            segments=segments_json,
        )

        response = format_search_response(len(segments), segments, quote)

        await self.__send_search_results(message, response, quote)

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer(get_no_segments_found_message(quote))
        await self._log_system_message(logging.INFO, get_log_no_segments_found_message(quote))

    async def __send_search_results(self, message: Message, response: str, quote: str) -> None:
        await self._answer_markdown(message , response)
        await self._log_system_message(logging.INFO, get_log_search_results_sent_message(quote, message.from_user.username))
