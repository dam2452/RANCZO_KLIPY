import logging
from aiogram import Router, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from bot.utils.db import is_user_authorized

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command('start'))
async def handle_start(message: Message):
    if not await is_user_authorized(message.from_user.username):
        await message.answer("Nie masz uprawnień do korzystania z tego bota.")
        return

    welcome_message = """
🐐 *Witaj w RanczoKlipy!* 🐐
Znajdź klipy z Twoich ulubionych momentów w prosty sposób. Oto, co możesz zrobić:

1️⃣ *Wyszukiwanie klipu na podstawie cytatu*:
    `/klip <cytat>` - Wyszukuje klip na podstawie cytatu. 
    Przykład: `/klip geniusz`.
    🔄 *Rozszerzenie wyniku*: `/rozszerz 1 3 2` (3s przed, 2s po).

2️⃣ *Znajdowanie klipów pasujących do cytatu*:
    `/szukaj <cytat>` - Znajduje klipy pasujące do cytatu. 
    Przykład: `/szukaj kozioł`.

3️⃣ *Wyświetlanie listy klipów*:
    `/lista` - Wyświetla listę klipów z informacjami: sezon, odcinek, data wydania.

4️⃣ *Pokazywanie wydłużonego klipu*:
    `/rozszerz <numer_klipu> <sekundy_wstecz> <sekundy_do_przodu>` - Pokazuje wydłużony klip na podstawie numeru klipu. 
    Przykład: `/rozszerz 1 3 2`.
    🔄 Możesz także użyć dwóch parametrów, aby wydłużyć ostatnio wybrany klip:
    `/rozszerz <sekundy_wstecz> <sekundy_do_przodu>` - Przykład: `/rozszerz 3 5`.

5️⃣ *Tworzenie kompilacji z wybranych klipów*:
    `/kompiluj <numery_klipów>` - Tworzy kompilację z wybranych klipów. 
    Przykłady: `/kompiluj 1,3,5` lub `/kompiluj 1-5` lub `/kompiluj wszystko`.

    🔎 *Szczegóły*:
    - `/szukaj` informuje o liczbie pasujących klipów.
    - `/lista` pokazuje klipy z opcją skróconej lub pełnej listy.
    - `/rozszerz` pozwala dokładniej zobaczyć klip, dodając sekundy przed i po.
    - `/kompiluj` umożliwia stworzenie kompilacji z wybranych klipów.

    💡 *Przykład rozszerzenia*:
    Aby zobaczyć klip nr 2 z dodatkowymi 2s przed i 3s po, wpisz: `/rozszerz 2 2 3`.
    Aby zobaczyć ostatnio wybrany klip z dodatkowymi 3s przed i 5s po, wpisz: `/rozszerz 3 5`.

    ⏳ Pamiętaj o limicie wydłużenia klipu o 20 sekund łącznie dla użytkowników bez specjalnych uprawnień.
    """
    await message.answer(welcome_message, parse_mode='Markdown')

def register_start_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
