import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import get_no_quote_provided_message, get_no_segments_found_message, get_transcription_response
from bot.utils.database import DatabaseManager
from bot.utils.transcription_search import SearchTranscriptions

class TranscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['transkrypcja', 'trans']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/transkrypcja {message.text}")
        content = message.text.split()
        if len(content) < 2:
            await message.answer(get_no_quote_provided_message())
            await self._log_system_message(logging.INFO, "No quote provided for transcription search.")
            return

        quote = ' '.join(content[1:])
        search_transcriptions = SearchTranscriptions()
        context_size = 15
        result = await search_transcriptions.find_segment_with_context(quote, context_size)

        if not result:
            await message.answer(get_no_segments_found_message(quote))
            await self._log_system_message(logging.INFO, f"No segments found for quote: '{quote}'")
            return

        context_segments = result['context']
        response = get_transcription_response(quote, context_segments)
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, f"Transcription for quote '{quote}' sent to user '{message.from_user.username}'.")
