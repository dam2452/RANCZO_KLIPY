import urllib3
from elasticsearch import Elasticsearch
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, filters
import os
from dotenv import load_dotenv

# Wyłączenie ostrzeżeń dotyczących certyfikatów SSL (zalecane tylko dla celów testowych)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Załadowanie zmiennych środowiskowych
load_dotenv("passwords.env")

es_host = os.getenv("ES_HOST")
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

es = Elasticsearch(
    [es_host],
    basic_auth=(es_username, es_password),
    verify_certs=False,
)


# Funkcja wyszukująca cytat w Elasticsearch
def search_quote(quote):
    body = {
        "query": {
            "match_phrase": {
                "text": quote
            }
        }
    }
    res = es.search(index="ranczo-transcriptions", body=body)
    return [(hit["_source"]["start"], hit["_source"]["end"], hit["_source"]["video_path"]) for hit in res['hits']['hits']]

# Funkcja ekstrahująca klip wideo
def extract_clip(episode_path, start_time, end_time, output_path):
    start_time = int(start_time)
    end_time = int(end_time)
    ffmpeg_extract_subclip(episode_path, start_time, end_time, targetname=output_path)

# Obsługa przychodzących wiadomości
def handle_message(update: Update, context: CallbackContext) -> None:
    quote = update.message.text
    results = search_quote(quote)
    if results:
        start, end, video_path = results[0]
        output_path = "output_clip.mp4"
        extract_clip(video_path, start, end, output_path)
        with open(output_path, 'rb') as video:
            context.bot.send_video(chat_id=update.message.chat_id, video=video)
        os.remove(output_path)
    else:
        update.message.reply_text('Nie znaleziono odpowiedniego fragmentu.')

# Główna funkcja bota
def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN, True)  # Ensure to pass use_context=True
    dispatcher = updater.dispatcher  # Access dispatcher via updater object

    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
