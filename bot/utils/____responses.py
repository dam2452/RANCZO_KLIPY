from datetime import date
from typing import (
    Dict,
    List,
    Union,
)

import asyncpg
from tabulate import tabulate




def format_subscription_status_response(username: str, subscription_end: date, days_remaining: int) -> str:
    return f"""
    ✨ **Status Twojej subskrypcji** ✨

    👤 **Użytkownik:** {username}
    📅 **Data zakończenia:** {subscription_end}
    ⏳ **Pozostało dni:** {days_remaining}

    Dzięki za wsparcie projektu! 🎉
    """








def get_basic_message() -> str:
    return """```🐐Witaj_w_RanczoKlipy!🐐
════════════════════════
🔍 Podstawowe komendy 🔍
════════════════════════
🔎 /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.
🔔 /subskrypcja - Sprawdza stan Twojej subskrypcji.

Aby uzyskać pełną listę komend, użyj /start lista.
```"""


def get_lista_message() -> str:
    return """```🐐RanczoKlipy-Działy_Komend🐐
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


def get_full_message() -> str:
    return """```🐐Witaj_w_RanczoKlipy!🐐
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


def get_wyszukiwanie_message() -> str:
    return """```🐐RanczoKlipy-Wyszukiwanie_klipów🐐
═════════════════════════════════════════
🔎 /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.
🔍 /szukaj <cytat> - Znajduje klipy pasujące do cytatu (pierwsze 5 wyników). Przykład: /szukaj kozioł.
📋 /lista - Wyświetla wszystkie klipy znalezione przez /szukaj.
✅ /wybierz <numer_klipu> - Wybiera klip z listy uzyskanej przez /szukaj do dalszych operacji. Przykład: /wybierz 1.
📺 /odcinki <sezon> - Wyświetla listę odcinków dla podanego sezonu. Przykład: /odcinki 2.
✂️ /wytnij <sezon_odcinek> <czas_start> <czas_koniec> - Wytnij fragment klipu. Przykład: /wytnij S02E10 20:30.11 21:32.50.
```"""


def get_edycja_message() -> str:
    return """```🐐RanczoKlipy-Edycja_klipów🐐
════════════════════
✂️ Edycja klipów ✂️
════════════════════
📏 /dostosuj <przedłużenie_przed> <przedłużenie_po> - Dostosowuje wybrany klip. Przykład: /dostosuj 5 5.
📏 /dostosuj <numer_klipu> <przedłużenie_przed> <przedłużenie_po> - Dostosowuje klip z wybranego zakresu. Przykład: /dostosuj 1 5 5.
🎞️ /kompiluj wszystko - Tworzy kompilację ze wszystkich klipów.
🎞️ /kompiluj <zakres> - Tworzy kompilację z zakresu klipów. Przykład: /kompiluj 1-4.
🎞️ /kompiluj <numer_klipu1> <numer_klipu2> ... - Tworzy kompilację z wybranych klipów. Przykład: /kompiluj 1 5 7.
```"""


def get_zarzadzanie_message() -> str:
    return """```🐐RanczoKlipy-Zarządzanie_zapisanymi_klipami🐐
═════════════════════════════════════
📁 Zarządzanie zapisanymi klipami 📁
═════════════════════════════════════
💾 /zapisz <nazwa> - Zapisuje wybrany klip z podaną nazwą. Przykład: /zapisz moj_klip.
📂 /mojeklipy - Wyświetla listę zapisanych klipów.
📤 /wyslij <nazwa> - Wysyła zapisany klip o podanej nazwie. Przykład: /wyslij moj_klip.
🔗 /polaczklipy <numer_klipu1> <numer_klipu2> ... - Łączy zapisane klipy w jeden. Numery klipów można znaleźć używając komendy /mojeklipy. Przykład: /polaczklipy 1 2 3.
🗑️ /usunklip <nazwa_klipu> - Usuwa zapisany klip o podanej nazwie. Przykład: /usunklip moj_klip.
```"""


def get_raportowanie_message() -> str:
    return """```🐐RanczoKlipy-Raportowanie_błędów🐐
════════════════════════
🛠️ Raportowanie błędów ️
════════════════════════
🐛 /report - Raportuje błąd do administratora.
```"""


def get_subskrypcje_message() -> str:
    return """```🐐RanczoKlipy-Subskrypcje🐐
══════════════════
🔔 Subskrypcje 🔔
══════════════════
📊 /subskrypcja - Sprawdza stan Twojej subskrypcji.
```"""







def get_user_removed_message(username: str) -> str:
    return f"✅ Usunięto {username} z whitelisty.✅"


def get_user_updated_message(username: str) -> str:
    return f"✅ Zaktualizowano dane użytkownika {username}.✅"





# fixme  tworzymy nowy folder "responses" i tam robimy np. delete_clip_responses.py dla kazdego handlera + generic wspoldzielone i WSZYSTKIE response'y mamy wyjebane do osobnych plikow i od razu wiadomo co zwraca ktory handler albo co jest wspoldzielone








def get_no_quote_provided_message() -> str:
    return "✏️ Podaj cytat, który chcesz znaleźć.✏️"


def get_no_segments_found_message(quote: str) -> str:
    return f"❌ Nie znaleziono pasujących segmentów dla cytatu: \"{quote}\".❌"


def get_transcription_response(quote: str, context_segments: List[Dict[str, Union[int, str]]]) -> str:
    response = f"🔍 Transkrypcja dla cytatu: \"{quote}\"\n\n```\n"
    for segment in context_segments:
        response += f"🆔 {segment['id']} - {segment['text']}\n"
    response += "```"
    return response







