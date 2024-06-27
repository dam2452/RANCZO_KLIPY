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
    ╔ ═════════════════════════════════════╗
    ║🔍 Wyszukiwanie i przeglądanie klipów:║
    ╚ ═════════════════════════════════════╝
 🔎 /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.
 🔍 /szukaj <cytat> - Znajduje klipy pasujące do cytatu (pierwsze 5 wyników). Przykład: /szukaj kozioł.
 📋 /lista - Wyświetla wszystkie klipy znalezione przez /szukaj.
 ✅ /wybierz <numer_klipu> - Wybiera klip z listy uzyskanej przez /szukaj do dalszych operacji. Przykład: /wybierz 1.
 
    ╔ ═════════════════════════════════════╗
    ║           ✂️ Edycja klipów:          ║
    ╚ ═════════════════════════════════════╝
 🔧 /rozszerz <numer_klipu> <wstecz> <do_przodu> - Pokazuje wydłużony klip na podstawie numeru klipu. Przykład: /rozszerz 1 3 2.
 🔧 /rozszerz <wstecz> <do_przodu> - Pokazuje wydłużony ostatnio wybrany klip. Przykład: /rozszerz 3 5.
 ✂️ /skroc <numer_klipu> <przed> <po> - Skraca klip na podstawie numeru klipu. Przykład: /skroc 1 2 1.
 ✂️ /skroc <przed> <po> - Skraca ostatnio wybrany klip. Przykład: /skroc 2 1.
 🎞️ /kompiluj wszystko - Tworzy kompilację ze wszystkich klipów.
 🎞️ /kompiluj <zakres> - Tworzy kompilację z zakresu klipów. Przykład: /kompiluj 1-4.
 🎞️ /kompiluj <numer_klipu1> <numer_klipu2> ... - Tworzy kompilację z wybranych klipów. Przykład: /kompiluj 1 5 7.
 
    ╔ ═════════════════════════════════════╗
    ║  📁 Zarządzanie zapisanymi klipami:  ║
    ╚ ═════════════════════════════════════╝
 💾 /zapisz <nazwa> - Zapisuje wybrany klip z podaną nazwą. Przykład: /zapisz moj_klip.
 📂 /mojeklipy - Wyświetla listę zapisanych klipów.
 📤 /wyslij <nazwa> - Wysyła zapisany klip o podanej nazwie. Przykład: /wyslij moj_klip.
 🔗 /polaczklipy <numer_klipu1> <numer_klipu2> ... - Łączy zapisane klipy w jeden. Numery klipów można znaleźć używając komendy /mojeklipy. Przykład: /polaczklipy 1 2 3.

    ╔ ═════════════════════════════════════╗
    ║        🛠️ Raportowanie błędów:       ║
    ╚ ═════════════════════════════════════╝
 🐛 /report - Raportuje błąd do administratora.
 
    ╔ ═════════════════════════════════════╗
    ║             🔔 Subskrypcje:          ║
    ╚ ═════════════════════════════════════╝
 📊 /subskrypcja - Sprawdza stan Twojej subskrypcji.
 
    ```"""

# """
# 2️⃣ /kupsuba - Kupuje subskrypcję.
# 3️⃣ /anulujsuba - Anuluje subskrypcję.
#
# """

    await message.answer(welcome_message, parse_mode='Markdown')

def register_start_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)

   # ╗  ╔ ═ ╣  ╚ ╝║