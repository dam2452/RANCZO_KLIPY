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
        await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.❌")
        return

    welcome_message = """```🐐Witaj_w_RanczoKlipy!🐐
    Znajdź klipy z Twoich ulubionych momentów w prosty sposób. Oto, co możesz zrobić:

    🔍 Wyszukiwanie i przeglądanie klipów:
 1️⃣ /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.
 2️⃣ /szukaj <cytat> - Znajduje klipy pasujące do cytatu (pierwsze 5 wyników). Przykład: /szukaj kozioł.
 3️⃣ /lista - Wyświetla wszystkie klipy znalezione przez /szukaj.
 4️⃣ /wybierz <numer_klipu> - Wybiera klip z listy uzyskanej przez /szukaj do dalszych operacji. Przykład: /wybierz 1.

    ✂️ Edycja klipów:
 1️⃣ /rozszerz <numer_klipu> <wstecz> <do_przodu> - Pokazuje wydłużony klip na podstawie numeru klipu. Przykład: /rozszerz 1 3 2.
 2️⃣ /rozszerz <wstecz> <do_przodu> - Pokazuje wydłużony ostatnio wybrany klip. Przykład: /rozszerz 3 5.
 3️⃣ /skroc <numer_klipu> <przed> <po> - Skraca klip na podstawie numeru klipu. Przykład: /skroc 1 2 1.
 4️⃣ /skroc <przed> <po> - Skraca ostatnio wybrany klip. Przykład: /skroc 2 1.
 5️⃣ /kompiluj wszystko - Tworzy kompilację ze wszystkich klipów.
 6️⃣ /kompiluj <zakres> - Tworzy kompilację z zakresu klipów. Przykład: /kompiluj 1-4.
 7️⃣ /kompiluj <numer_klipu1> <numer_klipu2> ... - Tworzy kompilację z wybranych klipów. Przykład: /kompiluj 1 5 7.

    📁 Zarządzanie zapisanymi klipami:
 1️⃣ /zapisz <nazwa> - Zapisuje wybrany klip z podaną nazwą. Przykład: /zapisz moj_klip.
 2️⃣ /mojeklipy - Wyświetla listę zapisanych klipów.
 3️⃣ /wyslij <nazwa> - Wysyła zapisany klip o podanej nazwie. Przykład: /wyslij moj_klip.
 4️⃣ /polaczklipy <numer_klipu1> <numer_klipu2> ... - Łączy zapisane klipy w jeden. Numery klipów można znaleźć używając komendy /mojeklipy. Przykład: /polaczklipy 1 2 3

    🛠️ Raportowanie błędów:
 1️⃣ /report - Raportuje błąd do administratora.

    🔔 Subskrypcje:
 1️⃣ /subskrypcja - Sprawdza stan Twojej subskrypcji.

    ```"""

# """
# 2️⃣ /kupsuba - Kupuje subskrypcję.
# 3️⃣ /anulujsuba - Anuluje subskrypcję.
#
# """

    await message.answer(welcome_message, parse_mode='Markdown')

def register_start_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
