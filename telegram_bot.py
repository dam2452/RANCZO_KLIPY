import os
import logging
from dotenv import load_dotenv
import telebot

from cache import get_cached_clip_path, clear_cache_by_age_and_limit
from search import find_segment_by_quote

# Wczytanie zmiennych środowiskowych z pliku .env, jeśli istnieje
load_dotenv('passwords.env')

# Konfiguracja i inicjalizacja bota
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Ustawienia loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globalny słownik do przechowywania ostatnich zapytań
last_search_quotes = {}

def send_clip_to_telegram(chat_id, episode_path, start_time, end_time):
    """
    Wysyła klip do użytkownika Telegrama.
    """
    output_path = get_cached_clip_path(episode_path, start_time, end_time)
    with open(output_path, 'rb') as video:
        bot.send_video(chat_id, video)


@bot.message_handler(commands=['klip'])
def handle_clip_request(message):
    quote = message.text[len('/klip '):].strip()  # Usuń '/klip ' i białe znaki z początku i końca
    logger.info(f"Searching for quote: '{quote}'")  # Dodaj log z wyszukiwanym cytatem
    segment = find_segment_by_quote(quote)

    if segment:
        logger.info(f"Found segment: {segment}")  # Logowanie znalezionego segmentu

        # Obliczanie numeru sezonu i odcinka w sezonie na podstawie ogólnego numeru odcinka
        total_episode_number = segment['episode_info']['episode_number']
        season_number = (total_episode_number - 1) // 13 + 1
        episode_number_in_season = (total_episode_number - 1) % 13 + 1



        # Tutaj powinna nastąpić logika wysyłająca klip, np.:
        send_clip_to_telegram(message.chat.id, segment['video_path'], segment['start'], segment['end'])
    else:
        logger.info(f"No matching segment found for quote: '{quote}'")
        bot.reply_to(message, "Nie znaleziono pasującego segmentu.")


@bot.message_handler(commands=['szukaj'])
def search_quotes(message):
    chat_id = message.chat.id
    content = message.text.split()
    if len(content) < 2:
        bot.reply_to(message, "Podaj cytat, który chcesz znaleźć.")
        return

    quote = ' '.join(content[1:])
    segments = find_segment_by_quote(quote, return_all=True)

    if not segments:
        bot.reply_to(message, "Nie znaleziono pasujących segmentów.")
        return

    response = f"Znaleziono {len(segments)} pasujących segmentów:\n"
    for segment in segments[:5]:  # Ograniczenie do pierwszych 5 wyników
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

        response += f"- {episode_formatted} {episode_title}, czas: {time_formatted}\n"

    bot.reply_to(message, response)


@bot.message_handler(commands=['lista'])
def list_segments(message):
    chat_id = message.chat.id  # Pobierz ID czatu
    content = message.text.split()
    all_segments = 'wszystko' in content

    if chat_id not in last_search_quotes:
        bot.reply_to(message, "Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        return

    quote = last_search_quotes[chat_id]
    segments = find_segment_by_quote(quote, return_all=True)

    if not segments:
        bot.reply_to(message, "Nie znaleziono segmentów dla ostatniego zapytania.")
        return

    if not all_segments:
        segments = segments[:5]

    response = "Lista segmentów:\n"
    for segment in segments:
        response += f"{segment['episode_info']['title']} (S{segment['episode_info']['season']}E{segment['episode_info']['episode_number']}): {segment['text']}\n"

    bot.reply_to(message, response)


@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_message = """
🎉 Witaj w RanczoKlipy! 🎉 Oto, jak możesz korzystać z bota:

1️⃣ /klip <cytat> - wyszukuje i wysyła klip na podstawie podanego cytatu. Np. /klip geniusz.
   - Możesz także rozszerzyć wynik: /rozszerz 1 2 (1s z przodu, 2s z tyłu).

2️⃣ /szukaj <cytat> [<filtr_sezonu> <filtr_odcinka>] - znajduje wszystkie klipy pasujące do cytatu. Np. /szukaj kozioł S01 lub /szukaj kozioł S01E02. Zwraca ilość wszystkich wystąpień oraz informacje o nich.

3️⃣ /lista [wszystko] - wyświetla listę znalezionych klipów wraz z numerami sezonów i odcinków (np. S01E01), nazwami odcinków, datami wydania itp. 
   - Użycie /lista pokaże 5 pierwszych wyników.
   - Użycie /lista wszystko wyświetli pełną listę wyników.

4️⃣ /rozszerz <numer_klipu> <sekundy_wstecz> <sekundy_do_przodu> - wyświetla wybrany klip, wydłużony o wskazaną liczbę sekund. Np. /rozszerz 1 3 2. 

5️⃣ /kompiluj <numery_klipów> - tworzy kompilację z wybranych klipów. Np. /kompiluj 1,3,5. 
   - Możesz także wybrać zakres: /kompiluj 1-5.
   - Użycie /kompiluj wszystko wybierze wszystkie znalezione klipy.

🔍 Szczegóły użycia:
- /szukaj poinformuje Cię, ile jest klipów odpowiadających zapytaniu. Możesz filtrować wyniki przez sezon lub sezon i numer odcinka.
- /lista pokaże Ci skróconą lub pełną listę znalezionych klipów, w zależności od wybranej opcji.
- /rozszerz pozwala na dokładniejsze zobaczenie klipu, dodając sekundy przed i po. Działa zarówno po użyciu /klip, jak i /szukaj.
- /kompiluj umożliwia stworzenie kompilacji z wybranych klipów. Możesz wybrać pojedyncze klipy, zakres lub wszystkie.

💡 Przykład rozszerzenia klipu:
Jeśli chcesz zobaczyć klip nr 2 z dodatkowymi 2 sekundami przed i 3 sekundami po, wpisz /rozszerz 2 2 3.

⏳ Pamiętaj, że każdy klip można maksymalnie wydłużyć o 10 sekund łącznie, po 5 sekund z każdej strony.
"""
    bot.reply_to(message, welcome_message)

# Czyszczenie cache
clear_cache_by_age_and_limit(90, 20000)

if __name__ == "__main__":
    logger.info("Bot started")
    bot.infinity_polling(interval=0, timeout=25)
