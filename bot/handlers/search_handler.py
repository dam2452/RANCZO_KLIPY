import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.global_dicts import (
    last_search_quotes,
    last_search_terms,
)
from bot.utils.transcription_search import SearchTranscriptions


class HandleSearchRequest(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['szukaj', 'search', 'sz']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/szukaj {message.text}")
        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            await self.__reply_no_quote_provided(message)
            return

        quote = ' '.join(content[1:])
        last_search_terms[chat_id] = quote

        search_transcriptions = SearchTranscriptions()

        segments = await search_transcriptions.find_segment_by_quote(quote, return_all=True)
        if not segments:
            await self.__reply_no_segments_found(message, quote)
            return

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

    async def __send_search_results(self, message: Message, response: str, quote: str) -> None:
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(
            logging.INFO,
            f"Search results for quote '{quote}' sent to user '{message.from_user.username}'.",
        )

    # todo jakiś specjalny błąd jak sie coś zjebie tylko nwm gdzie go dać
