from telebot import TeleBot
from ..utils.db import is_user_authorized

def register_start_handlers(bot: TeleBot):

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do korzystania z tego bota.")
            return

        welcome_message = """
🐐 *Witaj w RanczoKlipy!* 🐐
Znajdź klipy z Twoich ulubionych momentów w prosty sposób. Oto, co możesz zrobić:

1️⃣ `/klip <cytat>` - Wyszukuje klip na podstawie cytatu. 
Przykład: `/klip geniusz`.
🔄 *Rozszerzenie wyniku*: `/rozszerz 1 1 2` (1s przed, 2s po).

2️⃣ `/szukaj <cytat>` - Znajduje klipy pasujące do cytatu. 
Przykład: `/szukaj kozioł`.

3️⃣ `/lista` - Wyświetla listę klipów z informacjami: sezon, odcinek, data wydania.

4️⃣ `/rozszerz <numer_klipu> <sekundy_wstecz> <sekundy_do_przodu>` - Pokazuje wydłużony klip. 
Przykład: `/rozszerz 1 3 2`.

5️⃣ `/kompiluj <numery_klipów>` - Tworzy kompilację z wybranych klipów. 
Przykłady: `/kompiluj 1,3,5` lub `/kompiluj 1-5` lub `/kompiluj wszystko`.

🔎 *Szczegóły*:
- `/szukaj` informuje o liczbie pasujących klipów.
- `/lista` pokazuje klipy z opcją skróconej lub pełnej listy.
- `/rozszerz` pozwala dokładniej zobaczyć klip, dodając sekundy przed i po.
- `/kompiluj` umożliwia stworzenie kompilacji z wybranych klipów.

💡 *Przykład rozszerzenia*:
Aby zobaczyć klip nr 2 z dodatkowymi 2s przed i 3s po, wpisz: `/rozszerz 2 2 3`.

⏳ Pamiętaj o limicie wydłużenia klipu o 20 sekund łącznie.
"""
        bot.reply_to(message, welcome_message, parse_mode='Markdown')
