# cat bot.py
from cachetools.func import ttl_cache
import telebot
from elasticsearch import Elasticsearch
import os
import subprocess
import logging
import urllib3
import json
import time

# Załadowanie zmiennych środowiskowych
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env, jeśli istnieje
env_file = "passwords.env"
if os.path.exists(env_file):
    load_dotenv(env_file)

# Ścieżka do folderu cache
CACHE_DIR = os.path.join(os.getcwd(), "cache")

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


@ttl_cache(maxsize=100, ttl=3600)
def get_cached_clip_path(episode_path, start_time, end_time):
    clip_id = f"{os.path.basename(episode_path)}_{start_time}_{end_time}.mp4"
    output_path = os.path.join(CACHE_DIR, clip_id)

    if not os.path.exists(output_path):
        extract_clip(episode_path, start_time, end_time, output_path)

    return output_path

def clear_cache_by_age_and_limit(max_age_days=90, max_files=20000):
    current_time = time.time()
    files_and_times = []

    for filename in os.listdir(CACHE_DIR):
        if filename.endswith('.json'): continue  # Pomija pliki metadanych

        filepath = os.path.join(CACHE_DIR, filename)
        file_creation_time = os.path.getctime(filepath)
        age_days = (current_time - file_creation_time) / (60 * 60 * 24)
        files_and_times.append((filepath, file_creation_time, age_days))

    files_and_times.sort(key=lambda x: x[1])  # Sortuje od najstarszego

    # Usuwanie starych plików
    for filepath, _, age_days in files_and_times:
        if age_days > max_age_days or len(files_and_times) > max_files:
            os.remove(filepath)
            metadata_path = filepath + '.json'
            if os.path.exists(metadata_path): os.remove(metadata_path)
            files_and_times.remove((filepath, _, age_days))  # Aktualizuje listę

# Funkcja ekstrahująca klip wideo
def cache_clip_metadata(episode_path, start_time, end_time, output_path):
    metadata_path = output_path + '.json'
    metadata = {'episode_path': episode_path, 'start_time': start_time, 'end_time': end_time}
    with open(metadata_path, 'w') as f: json.dump(metadata, f)

def is_clip_cached(episode_path, start_time, end_time, output_path):
    metadata_path = output_path + '.json'
    if not os.path.exists(metadata_path) or not os.path.exists(output_path): return False
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata['episode_path'] == episode_path and metadata['start_time'] == start_time and metadata['end_time'] == end_time


def extract_clip(episode_path, start_time, end_time, output_path):
    adjusted_start_time, adjusted_end_time = max(int(start_time) - 2, 0), int(end_time) + 2
    if is_clip_cached(episode_path, adjusted_start_time, adjusted_end_time, output_path):
        print("Clip is already cached. Skipping extraction.")
        return True

    try:
        cmd = ["ffmpeg", "-y", "-ss", str(adjusted_start_time), "-i", episode_path, "-t", str(adjusted_end_time - adjusted_start_time),
               "-c:v", "libx264", "-crf", "25", "-profile:v", "main", "-c:a", "aac", "-b:a", "128k",
               "-ac", "2", "-preset", "superfast", "-movflags", "+faststart", "-loglevel", "error", output_path]
        subprocess.run(cmd, check=True)
        cache_clip_metadata(episode_path, adjusted_start_time, adjusted_end_time, output_path)
        print(f"Clip extracted and cached: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while extracting clip: {e}")
        return False
    return True

@ttl_cache(maxsize=100, ttl=3600)
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

    return hits[0]['_source']


def send_clip_to_telegram(chat_id, episode_path, start_time, end_time):
    output_path = get_cached_clip_path(episode_path, start_time, end_time)

    with open(output_path, 'rb') as video:
        bot.send_video(chat_id, video)



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

clear_cache_by_age_and_limit(90, 20000)
print("Bot started")
bot.infinity_polling(interval=0, timeout=25)