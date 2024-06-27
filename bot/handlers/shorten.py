# shorten.py
import logging
import os
import tempfile
from io import BytesIO
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.handlers.clip import last_selected_segment
from bot.utils.db import is_user_authorized
from bot.video_processing import extract_clip
from bot.handlers.search import last_search_quotes
from bot.handlers.expand import EXTEND_BEFORE, EXTEND_AFTER

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('skroc'))
async def handle_shorten_request(message: types.Message, bot: Bot):
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
            reduce_before = float(content[2])
            reduce_after = float(content[3])
            if chat_id not in last_search_quotes:
                await message.answer("Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
                return
            segments = last_search_quotes[chat_id]
            segment = segments[index]
        else:
            if chat_id not in last_selected_segment:
                await message.answer(
                    "Nie znaleziono żadnego wybranego segmentu. Użyj najpierw komendy /klip lub /wybierz.")
                return
            segment = last_selected_segment[chat_id]
            reduce_before = float(content[1])
            reduce_after = float(content[2])

        # Używaj rozszerzonych czasów z zapisanego segmentu
        original_start_time = segment['start'] - EXTEND_BEFORE
        original_end_time = segment['end'] + EXTEND_AFTER

        # Logowanie dla debugowania
        # logger.info("--------------------------------------------------------------------------------------------")
        # logger.info(f"Original start time: {original_start_time}, Original end time: {original_end_time}")
        # logger.info(f"Reduced by {reduce_before} seconds before and {reduce_after} seconds after")

        new_start_time = original_start_time + reduce_before
        new_end_time = original_end_time - reduce_after

        # logger.info(f"New start time: {new_start_time}, New end time: {new_end_time}")
        # logger.info("--------------------------------------------------------------------------------------------")

        # Upewnij się, że nowe czasy mieszczą się w oryginalnym zakresie klipu
        if new_start_time < 0 or new_end_time > original_end_time or new_start_time >= new_end_time:
            await message.answer("Nie można skrócić klipu, aby jego długość była równa lub mniejsza niż 0 lub poza zakresem oryginalnego klipu.")
            return

        video_path = segment['video_path']
        output_filename = os.path.join(tempfile.gettempdir(), f"{segment['id']}_shortened_clip.mp4")
        await extract_clip(video_path, new_start_time, new_end_time, output_filename)

        input_file = FSInputFile(output_filename)
        await bot.send_video(message.chat.id, input_file)
                             #caption=f"Skrócony klip: S{segment['episode_info']['season']}E{segment['episode_info']['episode_number']}")

        # Przechowuj skrócone czasy w segmentu
        segment['expanded_start'] = new_start_time
        segment['expanded_end'] = new_end_time

        # Przechowuj skrócony klip
        with open(output_filename, 'rb') as file:
            video_data = file.read()

        last_selected_segment[chat_id] = segment
        last_selected_segment[chat_id]['expanded_clip'] = BytesIO(video_data)

        os.remove(output_filename)

    except Exception as e:
        logger.error(f"Error handling /skroc command: {e}", exc_info=True)
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_shorten_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
