
import tempfile
import os
import logging
from dotenv import load_dotenv
import telebot

from cache import get_cached_clip_path, clear_cache_by_age_and_limit
from search import find_segment_by_quote
from cache import get_cached_clip_path, clear_cache_by_age_and_limit, compile_clips_into_one  # Dodaj import


load_dotenv('passwords.env')

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globalny słownik do przechowywania informacji o ostatnio wybranym/znalezionym segmencie dla każdego chat_id
last_selected_segment = {}
last_search_quotes = {}

def send_clip_to_telegram(chat_id, video_path, start_time, end_time):
    """
    Retrieve the cached clip and send it to the Telegram user.
    """
    try:
        clip_path = get_cached_clip_path(video_path, start_time, end_time)
        with open(clip_path, 'rb') as video:
            bot.send_video(chat_id, video)
        logger.info(f"Sent video clip from {start_time} to {end_time} to chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send video clip: {e}")
@bot.message_handler(commands=['klip'])
def handle_clip_request(message):
    """Handles a clip request command from a Telegram chat.

    Extracts a quote from the message text following the '/klip' command and searches for a video segment
    corresponding to the quote. If found, sends the clip to the chat; otherwise, notifies the user that
    no segment was found.
    """
    chat_id = message.chat.id
    quote = message.text[len('/klip '):].strip()  # Remove '/klip ' and leading/trailing whitespace
    if not quote:
        bot.reply_to(message, "Please provide a quote after the '/klip' command.")
        return
    logger.info(f"Searching for quote: '{quote}'")
    segments = find_segment_by_quote(quote, return_all=True)

    if segments:
        segment = segments[0]
        last_selected_segment[chat_id] = segment  # Zapisanie segmentu
        logger.info(f"Found segment: {segment}")
        send_clip_to_telegram(message.chat.id, segment['video_path'], segment['start'], segment['end'])
    else:
        logger.info(f"No segment found for quote: '{quote}'")
        bot.reply_to(message, "No segment found for the given quote.")
@bot.message_handler(commands=['szukaj'])
def search_quotes(message):
    """Searches for video segments matching a given quote from a Telegram message.

    Parses the message to extract a quote and optional season and episode filters. Searches for segments
    matching the quote and filters. Replies with the found segments or a message indicating none were found.
    """
    chat_id = message.chat.id
    content = message.text.split()
    if len(content) < 2:
        bot.reply_to(message, "Podaj cytat, który chcesz znaleźć.")
        return

    quote = ' '.join(content[1:])
    season_filter = content[2] if len(content) > 2 else None
    episode_filter = content[3] if len(content) > 3 else None
    segments = find_segment_by_quote(quote, season_filter, episode_filter, return_all=True)

    if not segments:
        bot.reply_to(message, "Nie znaleziono pasujących segmentów.")
        return

    # Update last_search_quotes with the current user's chat ID and quote
    last_search_quotes[chat_id] = segments


    response = f"Znaleziono {len(segments)} pasujących segmentów:\n"
    for i, segment in enumerate(segments[:5], start=1):  # Ograniczenie do pierwszych 5 wyników
        # Przeliczanie na podstawie ogólnego numeru odcinka
        total_episode_number = segment['episode_info']['episode_number']
        season_number = (total_episode_number - 1) // 13 + 1  # Obliczanie numeru sezonu
        episode_number_in_season = (total_episode_number - 1) % 13 + 1  # Obliczanie numeru odcinka w sezonie

        season = str(season_number).zfill(2)
        episode_number = str(episode_number_in_season).zfill(2)
        episode_title = segment['episode_info']['title']
        start_time = int(segment['start'])
        minutes, seconds = divmod(start_time, 60)
        time_formatted = f"{minutes:02}:{seconds:02}"

        episode_formatted = f"S{season}E{episode_number}"

        response += f"{i}. {episode_formatted} {episode_title}, czas: {time_formatted}\n"

    bot.reply_to(message, response)
@bot.message_handler(commands=['lista'])
def list_all_quotes(message):
    """Lists all quotes found from a user's last search.

    Checks if there were any segments found from the user's last search and responds accordingly.
    If segments were found, it formats a detailed message with the segments' information and sends
    it as a document to the user.
    """
    chat_id = message.chat.id
    if chat_id not in last_search_quotes:
        bot.reply_to(message, "Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        return

    segments = last_search_quotes[chat_id]

    if not segments:
        bot.reply_to(message, "Nie znaleziono pasujących segmentów.")
        return

    response = f"Znaleziono {len(segments)} pasujących segmentów:\n"
    for i, segment in enumerate(segments, start=1):
        total_episode_number = segment['episode_info']['episode_number']
        season_number = (total_episode_number - 1) // 13 + 1  # Przykładowe obliczenie numeru sezonu
        episode_number_in_season = (total_episode_number - 1) % 13 + 1  # Przykładowe obliczenie numeru odcinka w sezonie

        season = str(season_number).zfill(2)
        episode_number = str(episode_number_in_season).zfill(2)
        episode_title = segment['episode_info']['title']
        start_time = int(segment['start'])
        minutes, seconds = divmod(start_time, 60)
        time_formatted = f"{minutes:02}:{seconds:02}"

        episode_formatted = f"S{season}E{episode_number}"

        response += f"{i}. {episode_formatted} {episode_title}, czas: {time_formatted}\n"

    temp_dir = tempfile.gettempdir()
    file_name = os.path.join(temp_dir, f"quote_results_chat_{chat_id}.txt")
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(response)

    try:
        with open(file_name, 'rb') as file:
            bot.send_document(chat_id, file)
    finally:
        os.remove(file_name)
@bot.message_handler(commands=['wybierz'])
def select_quote(message):
    """
    Allows the user to select a specific quote segment from their last search results.

    This function checks if the user has previously performed a search. If so, it then
    verifies if the user provided a valid segment number. Finally, it sends the selected
    video clip to the user.
    """
    chat_id = message.chat.id
    # Sprawdź, czy dla tego chat_id wykonano już jakieś wyszukiwanie
    if chat_id not in last_search_quotes:
        bot.reply_to(message, "Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        return

    content = message.text.split()
    # Sprawdź, czy użytkownik podał numer segmentu do wybrania
    if len(content) < 2:
        bot.reply_to(message, "Podaj numer segmentu, który chcesz wybrać.")
        return

    try:
        segment_number = int(content[1])
    except ValueError:
        bot.reply_to(message, "Numer segmentu musi być liczbą.")
        return

    # Pobierz segmenty znalezione w ostatnim wyszukiwaniu
    segments = last_search_quotes[chat_id]

    # Sprawdź, czy podany numer segmentu jest prawidłowy
    if segment_number < 1 or segment_number > len(segments):
        bot.reply_to(message, "Nieprawidłowy numer segmentu.")
        return

    # Wybierz segment na podstawie podanego numeru
    segment = segments[segment_number - 1]

    # Zapisz wybrany segment do last_selected_segment dla późniejszego użycia
    last_selected_segment[chat_id] = segment

    # Wysyłka wybranego klipu do użytkownika
    send_clip_to_telegram(chat_id, segment['video_path'], segment['start'], segment['end'])
@bot.message_handler(commands=['rozszerz'])
def expand_clip(message):
    """
    Expands the duration of a previously selected video clip by adding extra time before and after it.

    Users specify the number of seconds to add before and after the original segment. This function
    first checks if the necessary parameters are provided and validates them. Then, it checks if there's
    a previously selected segment to expand. If all conditions are met, it sends the expanded clip to the user.
    """
    chat_id = message.chat.id
    content = message.text.split()
    # Sprawdzenie, czy podano odpowiednią ilość argumentów
    if len(content) < 4:
        bot.reply_to(message, "Podaj numer segmentu i ilość sekund do dodania przed i po klipie.")
        return

    try:
        segment_number = int(content[1])
        seconds_before = int(content[2])
        seconds_after = int(content[3])
    except ValueError:
        bot.reply_to(message, "Numer segmentu i ilość sekund muszą być liczbami.")
        return

    # Sprawdzenie, czy istnieje ostatnio wybrany segment
    if chat_id not in last_selected_segment:
        bot.reply_to(message, "Najpierw użyj /klip lub /wybierz, aby znaleźć klip.")
        return

    segment = last_selected_segment[chat_id]
    # Wysyłka rozszerzonego klipu do użytkownika
    send_clip_to_telegram(chat_id, segment['video_path'], segment['start'] - seconds_before, segment['end'] + seconds_after)
@bot.message_handler(commands=['kompiluj'])
def compile_clips(message):
    """
    Compiles multiple video segments into a single video clip.

    This function allows users to specify which segments to compile by providing individual segment
    indexes, a range of indexes, or a keyword to compile all segments. It checks for a previous search
    to ensure there are segments to compile. Then, based on the user's input, it selects the appropriate
    segments and compiles them into one video clip.
    """
    chat_id = message.chat.id
    content = message.text.split()

    # Check if there are any segments to compile
    if chat_id not in last_search_quotes or not last_search_quotes[chat_id]:
        bot.reply_to(message, "Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        return

    segments = last_search_quotes[chat_id]

    # Determine if user wants to compile all segments
    if len(content) == 2 and content[1].lower() == "wszystko":
        selected_segments = segments
    elif len(content) >= 2:
        selected_segments = []
        for index in content[1:]:
            if '-' in index:  # Check if it's a range
                start, end = map(int, index.split('-'))
                selected_segments.extend(segments[start-1:end])  # Convert to 0-based index and include end
            else:
                try:
                    selected_segments.append(segments[int(index) - 1])  # Convert to 0-based index
                except (ValueError, IndexError):
                    bot.reply_to(message, f"Podano nieprawidłowy indeks segmentu: {index}")
                    return
    else:
        bot.reply_to(message, "Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów.")
        return

    compile_clips_into_one(selected_segments, chat_id, bot)
@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_message = """
🐐 *Witaj w RanczoKlipy!* 🐐
Znajdź klipy z Twoich ulubionych momentów w prosty sposób. Oto, co możesz zrobić:

1️⃣ `/klip <cytat>` - Wyszukuje klip na podstawie cytatu. \
Przykład: `/klip geniusz`.
   🔄 *Rozszerzenie wyniku*: `/rozszerz 1 1 2` (1s przed, 2s po).

2️⃣ `/szukaj <cytat>` - Znajduje klipy pasujące do cytatu. \
Przykład: `/szukaj kozioł`.

3️⃣ `/lista` - Wyświetla listę klipów z informacjami: sezon, odcinek, data wydania.

4️⃣ `/rozszerz <numer_klipu> <sekundy_wstecz> <sekundy_do_przodu>` - Pokazuje wydłużony klip. \
Przykład: `/rozszerz 1 3 2`.

5️⃣ `/kompiluj <numery_klipów>` - Tworzy kompilację z wybranych klipów. \
Przykłady: `/kompiluj 1,3,5` lub `/kompiluj 1-5` lub `/kompiluj wszystko`.

🔎 *Szczegóły*:
- `/szukaj` informuje o liczbie pasujących klipów.
- `/lista` pokazuje klipy z opcją skróconej lub pełnej listy.
- `/rozszerz` pozwala dokładniej zobaczyć klip, dodając sekundy przed i po.
- `/kompiluj` umożliwia stworzenie kompilacji z wybranych klipów.

💡 *Przykład rozszerzenia*:
Aby zobaczyć klip nr 2 z dodatkowymi 2s przed i 3s po, wpisz: `/rozszerz 2 2 3`.

⏳ Pamiętaj o limicie wydłużenia klipu o 10 sekund łącznie, maksymalnie 5 sekund z każdej strony.
"""
    bot.reply_to(message, welcome_message, parse_mode='Markdown')

# Czyszczenie cache
clear_cache_by_age_and_limit(90, 20000)

if __name__ == "__main__":
    logger.info("Bot started")
    try:
        bot.infinity_polling(interval=0, timeout=25)
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
    finally:
        clear_cache_by_age_and_limit(90, 20000)
        logger.info("Cache cleared")
