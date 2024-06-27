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
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.")
            logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) not in (3, 4):
            await message.answer("✂️ Podaj numer klipu (opcjonalnie), sekundy przed i sekundy po. Przykład: /skroc 1 5 5")
            logger.info("Invalid number of arguments provided by user.")
            return

        if len(content) == 4:
            index = int(content[1]) - 1
            reduce_before = float(content[2])
            reduce_after = float(content[3])
            if chat_id not in last_search_quotes:
                await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
                logger.info("No previous search results found for user.")
                return
            segments = last_search_quotes[chat_id]
            segment = segments[index]
        else:
            if chat_id not in last_selected_segment:
                await message.answer("❌ Nie znaleziono żadnego wybranego segmentu. Użyj najpierw komendy /klip lub /wybierz.")
                logger.info("No previously selected segment found for user.")
                return
            segment = last_selected_segment[chat_id]
            reduce_before = float(content[1])
            reduce_after = float(content[2])

        original_start_time = segment['start'] - EXTEND_BEFORE
        original_end_time = segment['end'] + EXTEND_AFTER

        new_start_time = original_start_time + reduce_before
        new_end_time = original_end_time - reduce_after

        if new_start_time < 0 or new_end_time > original_end_time or new_start_time >= new_end_time:
            await message.answer("❌ Nie można skrócić klipu poza zakres oryginalnego klipu lub do długości równej lub mniejszej niż 0.")
            logger.warning(f"Invalid shorten request: new start time {new_start_time}, new end time {new_end_time}")
            return

        video_path = segment['video_path']
        output_filename = os.path.join(tempfile.gettempdir(), f"{segment['id']}_shortened_clip.mp4")
        await extract_clip(video_path, new_start_time, new_end_time, output_filename)

        input_file = FSInputFile(output_filename)
        await bot.send_video(message.chat.id, input_file) #caption="✂️ Skrócony klip! ✂️")

        segment['expanded_start'] = new_start_time
        segment['expanded_end'] = new_end_time

        with open(output_filename, 'rb') as file:
            video_data = file.read()

        last_selected_segment[chat_id] = segment
        last_selected_segment[chat_id]['expanded_clip'] = BytesIO(video_data)

        os.remove(output_filename)
        logger.info(f"Shortened clip for segment {segment['id']} sent to user '{message.from_user.username}'.")

    except Exception as e:
        logger.error(f"Error handling /skroc command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.")

def register_shorten_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
