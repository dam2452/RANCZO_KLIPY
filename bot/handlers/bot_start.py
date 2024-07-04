import logging
from aiogram import Router, Dispatcher, types, Bot
from aiogram.filters import Command
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command(commands=['start', 's', 'help', 'h']))
async def handle_start(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username
        content = message.text.split()
        if len(content) == 1:
            basic_message = """```🐐Witaj_w_RanczoKlipy!🐐
════════════════════════
🔍 Podstawowe komendy 🔍
════════════════════════
🔎 /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.
🔔 /subskrypcja - Sprawdza stan Twojej subskrypcji.

Aby uzyskać pełną listę komend, użyj /start lista.
```"""
            await message.answer(basic_message, parse_mode='Markdown')
            logger.info(f"Basic start message sent to user '{username}'.")

        elif len(content) == 2 and content[1] == 'lista':
            lista_message = """```🐐RanczoKlipy-Działy_Komend🐐
═══════════════════════════════════════
🔍 Wyszukiwanie i przeglądanie klipów 
👉 /start wyszukiwanie
═══════════════════════════════════════
✂️ Edycja klipów                      
👉 /start edycja
═══════════════════════════════════════
📁 Zarządzanie zapisanymi klipami     
👉 /start zarządzanie
═══════════════════════════════════════
🛠️ Raportowanie błędów              
👉 /start raportowanie  
═══════════════════════════════════════
🔔 Subskrypcje                       
👉 /start subskrypcje
═══════════════════════════════════════
📜 Wszystkie komendy                 
👉 /start all
═══════════════════════════════════════
```"""
            await message.answer(lista_message, parse_mode='Markdown')
            logger.info(f"List of sections sent to user '{username}'.")

        elif len(content) == 2 and content[1] == 'all':
            full_message = """```🐐Witaj_w_RanczoKlipy!🐐
═════════════════════════════════════════
🔍 Wyszukiwanie i przeglądanie klipów 🔍
═════════════════════════════════════════
🔎 /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.
🔍 /szukaj <cytat> - Znajduje klipy pasujące do cytatu (pierwsze 5 wyników). Przykład: /szukaj kozioł.
📋 /lista - Wyświetla wszystkie klipy znalezione przez /szukaj.
✅ /wybierz <numer_klipu> - Wybiera klip z listy uzyskanej przez /szukaj do dalszych operacji. Przykład: /wybierz 1.
📺 /odcinki <sezon> - Wyświetla listę odcinków dla podanego sezonu. Przykład: /odcinki 2.
✂️ /wytnij <sezon_odcinek> <czas_start> <czas_koniec> - Wytnij fragment klipu. Przykład: /wytnij S02E10 20:30.11 21:32.50.

════════════════════
✂️ Edycja klipów ✂️
════════════════════
📏 /dostosuj <przedłużenie_przed> <przedłużenie_po> - Dostosowuje wybrany klip. Przykład: /dostosuj 5 5.
📏 /dostosuj <numer_klipu> <przedłużenie_przed> <przedłużenie_po> - Dostosowuje klip z wybranego zakresu. Przykład: /dostosuj 1 5 5.
🎞️ /kompiluj wszystko - Tworzy kompilację ze wszystkich klipów.
🎞️ /kompiluj <zakres> - Tworzy kompilację z zakresu klipów. Przykład: /kompiluj 1-4.
🎞️ /kompiluj <numer_klipu1> <numer_klipu2> ... - Tworzy kompilację z wybranych klipów. Przykład: /kompiluj 1 5 7.

═════════════════════════════════════
📁 Zarządzanie zapisanymi klipami 📁
═════════════════════════════════════
💾 /zapisz <nazwa> - Zapisuje wybrany klip z podaną nazwą. Przykład: /zapisz moj_klip.
📂 /mojeklipy - Wyświetla listę zapisanych klipów.
📤 /wyslij <nazwa> - Wysyła zapisany klip o podanej nazwie. Przykład: /wyslij moj_klip.
🔗 /polaczklipy <numer_klipu1> <numer_klipu2> ... - Łączy zapisane klipy w jeden. Numery klipów można znaleźć używając komendy /mojeklipy. Przykład: /polaczklipy 1 2 3.
🗑️ /usunklip <nazwa_klipu> - Usuwa zapisany klip o podanej nazwie. Przykład: /usunklip moj_klip.

════════════════════════
🛠️ Raportowanie błędów ️
════════════════════════
🐛 /report - Raportuje błąd do administratora.

══════════════════
🔔 Subskrypcje 🔔
══════════════════
📊 /subskrypcja - Sprawdza stan Twojej subskrypcji.
```"""
            await message.answer(full_message, parse_mode='Markdown')
            logger.info(f"Full start message sent to user '{username}'.")

        elif len(content) == 2 and content[1] == 'wyszukiwanie':
            wyszukiwanie_message = """```🐐RanczoKlipy-Wyszukiwanie_i_przeglądanie_klipów🐐
═════════════════════════════════════════
🔎 /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.
🔍 /szukaj <cytat> - Znajduje klipy pasujące do cytatu (pierwsze 5 wyników). Przykład: /szukaj kozioł.
📋 /lista - Wyświetla wszystkie klipy znalezione przez /szukaj.
✅ /wybierz <numer_klipu> - Wybiera klip z listy uzyskanej przez /szukaj do dalszych operacji. Przykład: /wybierz 1.
📺 /odcinki <sezon> - Wyświetla listę odcinków dla podanego sezonu. Przykład: /odcinki 2.
✂️ /wytnij <sezon_odcinek> <czas_start> <czas_koniec> - Wytnij fragment klipu. Przykład: /wytnij S02E10 20:30.11 21:32.50.
```"""
            await message.answer(wyszukiwanie_message, parse_mode='Markdown')
            logger.info(f"Wyszukiwanie klipów message sent to user '{username}'.")

        elif len(content) == 2 and content[1] == 'edycja':
            edycja_message = """```🐐RanczoKlipy-Edycja_klipów🐐
════════════════════
✂️ Edycja klipów ✂️
════════════════════
📏 /dostosuj <przedłużenie_przed> <przedłużenie_po> - Dostosowuje wybrany klip. Przykład: /dostosuj 5 5.
📏 /dostosuj <numer_klipu> <przedłużenie_przed> <przedłużenie_po> - Dostosowuje klip z wybranego zakresu. Przykład: /dostosuj 1 5 5.
🎞️ /kompiluj wszystko - Tworzy kompilację ze wszystkich klipów.
🎞️ /kompiluj <zakres> - Tworzy kompilację z zakresu klipów. Przykład: /kompiluj 1-4.
🎞️ /kompiluj <numer_klipu1> <numer_klipu2> ... - Tworzy kompilację z wybranych klipów. Przykład: /kompiluj 1 5 7.
```"""
            await message.answer(edycja_message, parse_mode='Markdown')
            logger.info(f"Edycja klipów message sent to user '{username}'.")

        elif len(content) == 2 and content[1] == 'zarządzanie':
            zarzadzanie_message = """```🐐RanczoKlipy-Zarządzanie_zapisanymi_klipami🐐
═════════════════════════════════════
📁 Zarządzanie zapisanymi klipami 📁
═════════════════════════════════════
💾 /zapisz <nazwa> - Zapisuje wybrany klip z podaną nazwą. Przykład: /zapisz moj_klip.
📂 /mojeklipy - Wyświetla listę zapisanych klipów.
📤 /wyslij <nazwa> - Wysyła zapisany klip o podanej nazwie. Przykład: /wyslij moj_klip.
🔗 /polaczklipy <numer_klipu1> <numer_klipu2> ... - Łączy zapisane klipy w jeden. Numery klipów można znaleźć używając komendy /mojeklipy. Przykład: /polaczklipy 1 2 3.
🗑️ /usunklip <nazwa_klipu> - Usuwa zapisany klip o podanej nazwie. Przykład: /usunklip moj_klip.
```"""
            await message.answer(zarzadzanie_message, parse_mode='Markdown')
            logger.info(f"Zarządzanie zapisanymi klipami message sent to user '{username}'.")

        elif len(content) == 2 and content[1] == 'raportowanie':
            raportowanie_message = """```🐐RanczoKlipy-Raportowanie_błędów🐐
════════════════════════
🛠️ Raportowanie błędów ️
════════════════════════
🐛 /report - Raportuje błąd do administratora.
```"""
            await message.answer(raportowanie_message, parse_mode='Markdown')
            logger.info(f"Raportowanie błędów message sent to user '{username}'.")

        elif len(content) == 2 and content[1] == 'subskrypcje':
            subskrypcje_message = """```🐐RanczoKlipy-Subskrypcje🐐
══════════════════
🔔 Subskrypcje 🔔
══════════════════
📊 /subskrypcja - Sprawdza stan Twojej subskrypcji.
```"""
            await message.answer(subskrypcje_message, parse_mode='Markdown')
            logger.info(f"Subskrypcje message sent to user '{username}'.")

    except Exception as e:
        logger.error(f"Error in handle_start for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.")

def register_start_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
