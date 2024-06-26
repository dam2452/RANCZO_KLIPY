# start.py
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

5️⃣ *Skracanie klipu*:
    `/skroc <numer_klipu> <sekundy_przed> <sekundy_po>` - Skraca klip na podstawie numeru klipu. 
    Przykład: `/skroc 1 2 1`.

6️⃣ *Tworzenie kompilacji z wybranych klipów*:
    `/kompilujklipy <nazwy_klipów>` - Tworzy kompilację z wybranych klipów. 
    Przykład: `/kompilujklipy klip1 klip2 klip3`.

7️⃣ *Zapis klipu*:
    `/zapisz <nazwa_klipu>` - Zapisuje wybrany klip z podaną nazwą. 
    Przykład: `/zapisz moj_klip`.

8️⃣ *Wyświetlanie zapisanych klipów*:
    `/mojeklipy` - Wyświetla listę zapisanych klipów.

9️⃣ *Wysyłanie zapisanego klipu*:
    `/wyslijklip <nazwa_klipu>` - Wysyła zapisany klip o podanej nazwie. 
    Przykład: `/wyslijklip moj_klip`.

🔟 *Sprawdzanie subskrypcji*:
    `/mojasubskrypcja` - Sprawdza stan Twojej subskrypcji.
    """

    await message.answer(welcome_message, parse_mode='Markdown')

def register_start_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
