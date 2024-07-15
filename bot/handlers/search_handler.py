import logging
from typing import (
    Dict,
    List,
)

from aiogram.types import Message
from bot_message_handler import BotMessageHandler
from elastic_transport import ObjectApiResponse

from bot.utils.global_dicts import last_search
from bot.utils.transcription_search import SearchTranscriptions
from bot.handlers.responses.search_handler_responses import (
    get_invalid_args_count_message,
    get_no_segments_found_message,
    format_search_response,
    get_log_no_segments_found_message,
    get_log_search_results_sent_message
)


class SearchHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['szukaj', 'search', 'sz']

    async def _do_handle(self, message: Message) -> None:
        command = self.get_commands()[0]
        await self._log_user_activity(message.from_user.username, f"/{command} {message.text}")
        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        quote = ' '.join(content[1:])

        segments = await SearchTranscriptions.find_segment_by_quote(quote, return_all=True)
        if not segments:
            return await self.__reply_no_segments_found(message, quote)

        unique_segments = self.__get_unique_segments(segments)
        last_search[chat_id] = {'quote': quote, 'segments': list(unique_segments.values())}

        response = format_search_response(len(unique_segments), last_search[chat_id]['segments'])

        await self.__send_search_results(message, response, quote)

    @staticmethod
    def __get_unique_segments(segments: List[ObjectApiResponse]) -> Dict[str, ObjectApiResponse]:
        unique_segments = {}
        for segment in segments:
            episode_info = segment.get('episode_info', {})
            title = episode_info.get('title', 'Unknown')
            season = episode_info.get('season', 'Unknown')
            episode_number = episode_info.get('episode_number', 'Unknown')
            start_time = segment.get('start', 'Unknown')

            if season == 'Unknown' or episode_number == 'Unknown':
                continue

            unique_key = f"{title}-{season}-{episode_number}-{start_time}"
            if unique_key not in unique_segments:
                unique_segments[unique_key] = segment
        return unique_segments

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer(get_no_segments_found_message())
        await self._log_system_message(logging.INFO, get_log_no_segments_found_message(quote))

    async def __send_search_results(self, message: Message, response: str, quote: str) -> None:
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(
            logging.INFO,
            get_log_search_results_sent_message(quote, message.from_user.username),
        )
