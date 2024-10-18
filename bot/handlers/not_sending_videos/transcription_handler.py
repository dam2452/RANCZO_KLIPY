import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.bot_message_handler_responses import (
    get_log_no_segments_found_message,
    get_no_segments_found_message,
)
from bot.responses.not_sending_videos.transcription_handler_responses import (
    get_log_transcription_response_sent_message,
    get_no_quote_provided_message,
    get_transcription_response,
)
from bot.search.transcription_finder import TranscriptionFinder


class TranscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["transkrypcja", "transcription", "t"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__validate_quote_provided,
        ]

    async def __validate_quote_provided(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_no_quote_provided_message())
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        quote = " ".join(message.text.split()[1:])
        result = await TranscriptionFinder.find_segment_with_context(quote, self._logger, context_size=15)

        if not result:
            return await self.__reply_no_segments_found(message, quote)

        response = get_transcription_response(quote, result)
        await self.__reply_transcription_response(message, response, quote)

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await self._answer_markdown(message, get_no_segments_found_message(quote))
        await self._log_system_message(logging.INFO, get_log_no_segments_found_message(quote))

    async def __reply_transcription_response(self, message: Message, response: str, quote: str) -> None:
        await self._answer_markdown(message, response)
        await self._log_system_message(logging.INFO, get_log_transcription_response_sent_message(quote, message.from_user.username))
