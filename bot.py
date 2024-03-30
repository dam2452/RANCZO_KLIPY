import os
import subprocess
import telebot
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

if os.path.exists('passwords.env'):
    load_dotenv('passwords.env')

ES_HOST = os.getenv("ES_HOST")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Inicjalizacja bota
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Konfiguracja klienta Elasticsearch
es = Elasticsearch(
    [ES_HOST],
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=False,
)

user_results = {}

# Funkcja wyszukująca cytat w danym sezonie w Elasticsearch
def search_quote_in_season(quote, chat_id, season_number=None, episode_number=None):
    body = {
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "text": {
                            "query": quote,
                            "fuzziness": "AUTO"
                        }
                    }
                },
                "filter": []
            }
        },
        "size": 500  # Zwiększona liczba wyników
    }
    if season_number is not None:
        body["query"]["bool"]["filter"].append({
            "term": {
                "season": season_number
            }
        })
    if episode_number is not None:
        body["query"]["bool"]["filter"].append({
            "wildcard": {
                "video_path": f"*E{str(episode_number).zfill(2)}.json"
            }
        })

    res = es.search(index="ranczo-transcriptions", body=body)
    hits = res['hits']['hits']
    results = [{
        "start": hit["_source"]["start"],
        "end": hit["_source"]["end"],
        "video_path": hit["_source"]["video_path"]
    } for hit in hits]

    # Zapisz wyniki dla użytkownika
    user_results[chat_id] = results

    # Jeśli nie podano numeru sezonu, zwróć tylko pierwszy wynik
    if season_number is None:
        return results[:1]
    else:
        return results
@bot.message_handler(commands=['wybierz_klip'])
def handle_specific_clip_request(message):
    chat_id = message.chat.id
    args = message.text.split()[1:]

    # Sprawdź, czy wyniki dla użytkownika są dostępne
    if chat_id not in user_results or not user_results[chat_id]:
        bot.reply_to(message, "Brak zapisanych wyników wyszukiwania. Użyj najpierw /klip.")
        return

    try:
        selected_range = args[0]
        if "-" in selected_range:
            start, end = map(int, selected_range.split("-"))
            selected_results = user_results[chat_id][start - 1:end]
        else:
            selected_index = int(selected_range) - 1
            selected_results = [user_results[chat_id][selected_index]]

        # Wysyłanie wybranych klipów
        for result in selected_results:
            if extract_clip(result["video_path"], result["start"], result["end"], "output_clip.mp4"):
                with open("output_clip.mp4", 'rb') as video:
                    bot.send_video(message.chat.id, video)
                os.remove("output_clip.mp4")
            else:
                bot.reply_to(message, "Wystąpił błąd podczas ekstrakcji klipu.")
    except (ValueError, IndexError):
          bot.reply_to(message, "Nieprawidłowy format komendy lub numer poza zakresem.")

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
def handle_clip_command(message):
    process_clip_request(message)

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def handle_reply(message):
    process_clip_request(message, is_reply=True)


def process_clip_request(message, is_reply=False):
    chat_id = message.chat.id
    text = message.text.split(maxsplit=2)  # Rozdzielamy komendę na części

    if len(text) < 2:
        bot.reply_to(message, 'Użyj: /klip numer_sezonu "Twoje zapytanie"')
        return

    # Sprawdzamy, czy podano numer sezonu
    try:
        season_number = int(text[1])
        quote = text[2].strip('"')  # Usuwamy cudzysłowy z zapytania
    except ValueError:
        # Jeśli nie uda się przekonwertować na int, to oznacza, że pierwszy argument to cytat
        season_number = None
        quote = text[1].strip('"') if len(text) > 1 else ""

    if not quote:
        bot.reply_to(message,
                     'Nie podano zapytania. Użyj: /klip "Twoje zapytanie" lub /klip numer_sezonu "Twoje zapytanie"')
        return

    results = search_quote_in_season(quote, chat_id, season_number)
    if results:
        start = results[0]["start"]
        end = results[0]["end"]
        video_path = results[0]["video_path"]
        output_path = "output_clip.mp4"
        if extract_clip(video_path, start, end, output_path):
            with open(output_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove(output_path)
        else:
            bot.reply_to(message, 'Wystąpił błąd podczas ekstrakcji klipu.')
        if len(results) > 1:
            bot.send_message(chat_id, f'Znaleziono {len(results)} wyników. Użyj /wybierz_klip <numer> lub /wybierz_klip <zakres> aby wybrać konkretny wynik.')
    else:
        reply_message = 'Nie znaleziono odpowiedniego fragmentu'
        if season_number is not None:
            reply_message += f' w sezonie {season_number}'
        reply_message += '.'
        bot.reply_to(message, reply_message)

@bot.message_handler(commands=['ile_wynikow'])
def handle_results_count_command(message):
    chat_id = message.chat.id
    if chat_id in user_results and user_results[chat_id]:
        bot.send_message(chat_id, f'Znaleziono {len(user_results[chat_id])} wyników.')
    else:
        bot.send_message(chat_id, 'Brak zapisanych wyników wyszukiwania. Użyj najpierw /klip.')

print("Bot started")
bot.infinity_polling(interval=0, timeout=25)
