# cat bot.py  
import telebot
from elasticsearch import Elasticsearch
import os
import subprocess

# Załadowanie zmiennych środowiskowych
from dotenv import load_dotenv

load_dotenv("passwords.env")

es_host = os.getenv("ES_HOST")
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Konfiguracja klienta Elasticsearch
es = Elasticsearch(
    [es_host],
    basic_auth=(es_username, es_password),
    verify_certs=False,
)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Funkcja wyszukująca cytat w danym sezonie w Elasticsearch
def search_quote_in_season(quote, season_number=None):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": quote,
                            "fields": ["text"],
                            "fuzziness": "AUTO"
                        }
                    }
                ]
            }
        },
        "size": 1
    }
    if season_number is not None:
        body["query"]["bool"]["filter"] = [
            {"term": {"season": season_number}}
        ]
    res = es.search(index="ranczo-transcriptions", body=body)
    hits = res['hits']['hits']
    if hits:
        # Jeśli znaleziono dopasowanie, zwróć klip obejmujący wszystkie trafienia
        start = min(hit["_source"]["start"] for hit in hits) - 2  # Zapas 2s w obie strony
        end = max(hit["_source"]["end"] for hit in hits) + 2  # Zapas 2s w obie strony
        video_paths = [hit["_source"]["video_path"] for hit in hits]
        return start, end, video_paths[0]  # Zakładamy, że bierzemy tylko pierwszy klip
    else:
        return None, None, None

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

@bot.message_handler(commands=['klip'])
def handle_clip_request(message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        bot.reply_to(message, 'Użyj: /klip "Twoje zapytanie" lub /klip numer_sezonu "Twoje zapytanie"')
        return

    text = text[1]
    if text.startswith('"'):
        # Użytkownik wprowadził zapytanie w cudzysłowach, bez numeru sezonu
        try:
            quote = text.split('"')[1]
            season_number = None
        except IndexError:
            bot.reply_to(message, 'Nieprawidłowy format komendy. Użyj: /klip "Twoje zapytanie" lub /klip numer_sezonu "Twoje zapytanie"')
            return
    else:
        # Spróbuj odseparować numer sezonu od zapytania
        parts = text.split(maxsplit=1)
        if len(parts) == 2 and parts[1].startswith('"'):
            try:
                season_number = int(parts[0])
                quote = parts[1].split('"')[1]
            except (ValueError, IndexError):
                bot.reply_to(message, 'Nieprawidłowy format komendy. Użyj: /klip numer_sezonu "Twoje zapytanie"')
                return
        else:
            # Traktuj całość jako zapytanie bez numeru sezonu
            quote = text
            season_number = None

    start, end, video_path = search_quote_in_season(quote, season_number)
    if start is not None and end is not None and video_path is not None:
        output_path = "output_clip.mp4"
        if extract_clip(video_path, start, end, output_path):
            with open(output_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove(output_path)
        else:
            bot.reply_to(message, 'Wystąpił błąd podczas ekstrakcji klipu.')
    else:
        reply_message = 'Nie znaleziono odpowiedniego fragmentu'
        if season_number is not None:
            reply_message += f' w sezonie {season_number}'
        reply_message += '.'
        bot.reply_to(message, reply_message)

print("Bot started")
bot.infinity_polling(interval=0, timeout=25)