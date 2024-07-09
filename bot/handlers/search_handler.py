import json
import logging
from typing import (
    List,
    Dict,
)

from aiogram.types import Message

from bot_message_handler import BotMessageHandler

from bot.utils.database import DatabaseManager
from bot.utils.transcription_search import SearchTranscriptions


last_search_quotes: Dict[int, List[json]] = {}  #todo trzeba ta baze pod te sesje zrobić a nie się tak pierodlić
last_search_terms: Dict[int, str] = {}  #todo trzeba ta baze pod te sesje zrobić a nie się tak pierodlić


class HandleSearchRequest(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['szukaj', 'search', 'sz']

    def get_action_name(self) -> str:
        return "handle_search_request"

    async def _do_handle(self, message: Message) -> None:
        await self.__log_user_activity(message.from_user.username, f"/szukaj {message.text}")
        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            await self.__reply_no_quote_provided(message)
            return

        quote = ' '.join(content[1:])
        last_search_terms[chat_id] = quote

        search_transcriptions = SearchTranscriptions()  #fixme kurła jak to teraz wykonac jak ja nie mam tego dispatchera żeby przekazać temu do argmeuntu XD musze się wycztać mocniej jak dziłają te dispatchery
        segments = []  #fixme nie wiem czy to jest git w sensie cały ten try i wyjątek bo tam w klasie bazowej jest ten handle ale w adjust zrobiłeś ta funkcje z __ od tego i te try na koniec w /klip i /dostsuj wyjebalismy
        try:
            segments = await search_transcriptions.find_segment_by_quote(quote, return_all=True)
            if not segments:
                await self.__reply_no_segments_found(message, quote)
                return
        except Exception as e:
            await self.__log_error(message, e)

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

        last_search_quotes[chat_id] = list(unique_segments.values())

        response = f"🔍 Znaleziono {len(unique_segments)} pasujących segmentów:\n"
        segment_lines = []

        for i, segment in enumerate(last_search_quotes[chat_id][:5], start=1):
            episode_info = segment.get('episode_info', {})
            total_episode_number = episode_info.get('episode_number', 'Unknown')
            season_number = (total_episode_number - 1) // 13 + 1 if isinstance(total_episode_number, int) else 'Unknown'
            episode_number_in_season = (total_episode_number - 1) % 13 + 1 if isinstance(
                total_episode_number,
                int,
            ) else 'Unknown'

            season = str(season_number).zfill(2)
            episode_number = str(episode_number_in_season).zfill(2)
            episode_title = episode_info.get('title', 'Unknown')
            start_time = int(segment['start'])
            minutes, seconds = divmod(start_time, 60)
            time_formatted = f"{minutes:02}:{seconds:02}"

            episode_formatted = f"S{season}E{episode_number}"
            line = f"{i}️⃣ | 📺{episode_formatted} | 🕒 {time_formatted} \n👉  {episode_title} "
            segment_lines.append(line)

        response += "```\n" + "\n\n".join(segment_lines) + "\n```"

        await self.__send_search_results(message, response, quote)

    async def __reply_no_quote_provided(self, message: Message) -> None:
        await message.answer("🔍 Podaj cytat, który chcesz znaleźć. Przykład: /szukaj geniusz")
        await self._log_system_message(logging.INFO, "No search quote provided by user.")

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer("❌ Nie znaleziono pasujących cytatów.❌")
        await self._log_system_message(logging.INFO, f"No segments found for quote: '{quote}'")

    async def __log_user_activity(self, username: str, action: str) -> None:
        await DatabaseManager.log_user_activity(username, action)
        await self._log_system_message(logging.INFO, f"User '{username}' performed action: '{action}'")

    async def __log_error(self, message: Message, e: Exception) -> None:
        logger.error(f"Error in {self.get_action_name()} for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await self._log_system_message(logging.ERROR,
                                       f"Error in {self.get_action_name()} for user '{message.from_user.username}': {e}")

    async def __send_search_results(self, message: Message, response: str, quote: str) -> None:
        await message.answer(response, parse_mode='Markdown')
        logger.info(f"Search results for quote '{quote}' sent to user '{message.from_user.username}'.")
        await self._log_system_message(logging.INFO,
                                       f"Search results for quote '{quote}' sent to user '{message.from_user.username}'.")
