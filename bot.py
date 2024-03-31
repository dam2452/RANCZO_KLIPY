# cat bot.py  
import telebot
from elasticsearch import Elasticsearch
import os
import subprocess
import logging
import urllib3

# Załadowanie zmiennych środowiskowych
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env, jeśli istnieje
env_file = "passwords.env"
if os.path.exists(env_file):
    load_dotenv(env_file)

es_host = os.getenv("ES_HOST")
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wyłączenie ostrzeżenia dotyczącego niezaufanych żądań HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Funkcja do nawiązywania połączenia z Elasticsearch
def connect_elastic():
    """
    Funkcja do nawiązywania połączenia z Elasticsearch.
    """
    try:
        es = Elasticsearch(
            [es_host],
            http_auth=(es_username, es_password),
            verify_certs=False,  # Na potrzeby testów, w produkcji należy włączyć
        )
        if not es.ping():
            raise ValueError("Połączenie z Elasticsearch nie powiodło się.")
        logger.info("Połączono z Elasticsearch.")
        return es
    except Exception as e:
        logger.error(f"Nie udało się połączyć z Elasticsearch: {e}")
        return None

# Funkcja ekstrahująca klip wideo
def extract_clip(episode_path, start_time, end_time, output_path):
    start_time = max(int(start_time) - 2, 0)  # Zapas 2s w lewo
    end_time = int(end_time) + 2  # Zapas 2s w prawo
    duration = end_time - start_time
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", episode_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-crf", "25",  # Ustawienie CRF dla zmiennego bitrate wideo
            "-profile:v", "main",  # Profil "main" dla lepszej kompatybilności
            "-c:a", "aac",
            "-strict", "experimental",
            "-b:a", "128k",  # Stały bitrate dla audio
            "-ac", "2",  # Konwersja audio do stereo
            "-preset", "superfast",  # Najszybszy preset
            "-movflags", "+faststart",  # Umożliwia szybsze rozpoczęcie odtwarzania przez przeglądarki
            "-loglevel", "error",
            output_path
        ]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while extracting clip: {e}")
        return False
    return True

# Funkcja wysyłająca klip wideo do Telegrama
def find_segment_by_quote(quote, index='ranczo-transcriptions'):
    es = connect_elastic()

    query = {
        "query": {
            "match": {
                "text": {
                    "query": quote,
                    "fuzziness": "AUTO"
                }
            }
        }
    }

    response = es.search(index=index, body=query)
    hits = response['hits']['hits']

    if not hits:
        return None

    # Zwraca pierwszy pasujący segment
    return hits[0]['_source']

# Funkcja wysyłająca klip wideo do Telegrama
def send_clip_to_telegram(chat_id, episode_path, start_time, end_time):
    output_path = "temp_clip.mp4"
    extract_clip(episode_path, start_time, end_time, output_path)

    video = open(output_path, 'rb')
    bot.send_video(chat_id, video)
    video.close()


# Obsługa komendy /klip
@bot.message_handler(commands=['klip'])
def handle_clip_request(message):
    quote = message.text[len('/klip '):]  # Usuwa '/klip ' z początku wiadomości
    segment = find_segment_by_quote(quote)

    if segment:
        send_clip_to_telegram(message.chat.id, segment['video_path'], segment['start'], segment['end'])
    else:
        bot.reply_to(message, "Nie znaleziono pasującego segmentu.")

# Obsługa komendy /start
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


print("Bot started")
bot.infinity_polling(interval=0, timeout=25)