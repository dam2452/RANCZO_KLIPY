from elasticsearch import Elasticsearch
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import os

es = Elasticsearch(["http://192.168.0.210:30003"])

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def search_quote(quote):
    body = {
        "query": {
            "match_phrase": {
                "text": quote
            }
        }
    }
    res = es.search(index="ranczo-transcriptions", body=body)
    return [(hit["_source"]["start"], hit["_source"]["end"], hit["_source"]["video_path"]) for hit in
            res['hits']['hits']]

def extract_clip(episode_path, start_time, end_time, output_path):
    start_time = int(start_time)
    end_time = int(end_time)
    ffmpeg_extract_subclip(episode_path, start_time, end_time, targetname=output_path)

def handle_message(update, context):
    quote = update.message.text
    results = search_quote(quote)
    if results:
        start, end, video_path = results[0]
        output_path = "output_clip.mp4"
        extract_clip(video_path, start, end, output_path)
        update.message.reply_text('Oto Twój fragment!')
        with open(output_path, 'rb') as video:
            context.bot.send_video(chat_id=update.message.chat_id, video=video)
        os.remove(output_path)
    else:
        update.message.reply_text('Nie znaleziono odpowiedniego fragmentu.')

def main():
    if TELEGRAM_BOT_TOKEN is None:
        print("Nie znaleziono tokenu bota Telegram. Ustaw zmienną środowiskową TELEGRAM_BOT_TOKEN.")
        return
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(filters.text & ~filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
