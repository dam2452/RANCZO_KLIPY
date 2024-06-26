import logging
import os
import tempfile
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.handlers.clip import last_selected_segment
from bot.utils.db import is_user_authorized
from bot.video_processing import extract_clip
from bot.handlers.search import last_search_quotes

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('rozszerz'))
async def handle_expand_request(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) not in (3, 4):
            await message.answer("Podaj numer klipu (opcjonalnie), sekundy przed i sekundy po.")
            return

        if len(content) == 4:
            index = int(content[1]) - 1
            extra_before = int(content[2])
            extra_after = int(content[3])
            if chat_id not in last_search_quotes:
                await message.answer("Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
                return
            segments = last_search_quotes[chat_id]
            segment = segments[index]
        else:
            if chat_id not in last_selected_segment:
                await message.answer("Nie znaleziono żadnego wybranego segmentu. Użyj najpierw komendy /klip lub /wybierz.")
                return
            segment = last_selected_segment[chat_id]
            extra_before = int(content[1])
            extra_after = int(content[2])

        video_path = segment['video_path']
        start_time = max(0, segment['start'] - extra_before)
        end_time = segment['end'] + extra_after

        output_filename = os.path.join(tempfile.gettempdir(), f"{segment['id']}_expanded_clip.mp4")
        await extract_clip(video_path, start_time, end_time, output_filename)

        input_file = FSInputFile(output_filename)
        await bot.send_video(message.chat.id, input_file, caption=f"Rozszerzony klip: S{segment['episode_info']['season']}E{segment['episode_info']['episode_number']}")
        os.remove(output_filename)

    except Exception as e:
        logger.error(f"Error handling /rozszerz command: {e}", exc_info=True)
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_expand_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
