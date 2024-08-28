def get_basic_message() -> str:
    return """```🐐Witaj_w_RanczoKlipy!🐐
════════════════════════
🔍 Podstawowe komendy 🔍
════════════════════════
🔎 /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.
🔔 /subskrypcja - Sprawdza stan Twojej subskrypcji.
📜 /start lista - Wyświetla pełną listę komend.
```"""


def get_lista_message() -> str:
    return """```🐐 RanczoKlipy - Działy Komend 🐐
══════════════════════════
🔍 Wyszukiwanie:
   👉 /start wyszukiwanie

✂️ Edycja:
   👉 /start edycja

📁 Zarządzanie:
   👉 /start zarzadzanie

🛠️ Raporty:
   👉 /start raportowanie

🔔 Subskrypcje:
   👉 /start subskrypcje

📜 Wszystkie:
   👉 /start wszystko

📋 Skróty:
   👉 /start skroty
══════════════════════════
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
📏 /dostosuj <przedłużenie_przed> <przedłużenie_po> - Dostosowuje wybrany klip. Przykład: /dostosuj -5.5 1.2.
📏 /dostosuj <numer_klipu> <przedłużenie_przed> <przedłużenie_po> - Dostosowuje klip z wybranego zakresu. Przykład: /dostosuj 1 10.0 -3.
🎞️ /kompiluj wszystko - Tworzy kompilację ze wszystkich klipów.
🎞️ /kompiluj <zakres> - Tworzy kompilację z zakresu klipów. Przykład: /kompiluj 1-4.
🎞️ /kompiluj <numer_klipu1> <numer_klipu2> ... - Tworzy kompilację z wybranych klipów. Przykład: /kompiluj 1 5 7.

═════════════════════════════════════
📁 Zarządzanie zapisanymi klipami 📁
═════════════════════════════════════
💾 /zapisz <nazwa> - Zapisuje wybrany klip z podaną nazwą. Przykład: /zapisz moj_klip.
📂 /mojeklipy - Wyświetla listę zapisanych klipów.
📤 /wyslij <nazwa> - Wysyła zapisany klip o podanej nazwie. Przykład: /wyslij moj_klip.
🔗 /polaczklipy <nazwa_klipu1> <nazwa_klipu2> ... - Łączy zapisane klipy w jeden. Numery klipów można znaleźć używając komendy /mojeklipy. Przykład: /polaczklipy nazwa1 nazwa2 nazwa3.
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
════════════════════
🔍 Wyszukiwanie 🔍
════════════════════

🔎 /klip <cytat> - Wyszukuje klip na podstawie cytatu. Przykład: /klip geniusz.\n
🔍 /szukaj <cytat> - Znajduje klipy pasujące do cytatu (pierwsze 5 wyników). Przykład: /szukaj kozioł.\n
📋 /lista - Wyświetla wszystkie klipy znalezione przez /szukaj.\n
✅ /wybierz <numer_klipu> - Wybiera klip z listy uzyskanej przez /szukaj do dalszych operacji. Przykład: /wybierz 1.\n
📺 /odcinki <sezon> - Wyświetla listę odcinków dla podanego sezonu. Przykład: /odcinki 2.\n
✂️ /wytnij <sezon_odcinek> <czas_start> <czas_koniec> - Wytnij fragment klipu. Przykład: /wytnij S02E10 20:30.11 21:32.50.\n
```"""


def get_edycja_message() -> str:
    return """```🐐RanczoKlipy-Edycja_klipów🐐
════════════════════
✂️ Edycja klipów ✂️
════════════════════
📏 /dostosuj <przedłużenie_przed> <przedłużenie_po> - Dostosowuje wybrany klip. Przykład: /dostosuj -5.5 1.2.\n
📏 /dostosuj <numer_klipu> <przedłużenie_przed> <przedłużenie_po> - Dostosowuje klip z wybranego zakresu. Przykład: /dostosuj 1 10.0 -3.\n
🎞️ /kompiluj wszystko - Tworzy kompilację ze wszystkich klipów.\n
🎞️ /kompiluj <zakres> - Tworzy kompilację z zakresu klipów. Przykład: /kompiluj 1-4.\n
🎞️ /kompiluj <numer_klipu1> <numer_klipu2> ... - Tworzy kompilację z wybranych klipów. Przykład: /kompiluj 1 5 7.\n
```"""


def get_zarzadzanie_message() -> str:
    return """```🐐RanczoKlipy-Zarządzanie_zapisanymi_klipami🐐
═════════════════════════════════════
📁 Zarządzanie zapisanymi klipami 📁
═════════════════════════════════════
💾 /zapisz <nazwa> - Zapisuje wybrany klip z podaną nazwą. Przykład: /zapisz moj_klip.\n
📂 /mojeklipy - Wyświetla listę zapisanych klipów.\n
📤 /wyslij <nazwa> - Wysyła zapisany klip o podanej nazwie. Przykład: /wyslij moj_klip.\n
🔗 /polaczklipy <nazwa_klipu1> <nazwa_klipu2> ... - Łączy zapisane klipy w jeden. Numery klipów można znaleźć używając komendy /mojeklipy. Przykład: /polaczklipy nazwa1 nazwa2 nazwa3.\n
🗑️ /usunklip <nazwa_klipu> - Usuwa zapisany klip o podanej nazwie. Przykład: /usunklip moj_klip.\n
```"""


def get_raportowanie_message() -> str:
    return """```🐐RanczoKlipy-Raportowanie_błędów🐐
════════════════════════
🛠️ Raportowanie błędów ️
════════════════════════
🐛 /report - Raportuje błąd do administratora.\n
```"""


def get_subskrypcje_message() -> str:
    return """```🐐RanczoKlipy-Subskrypcje🐐
══════════════════
🔔 Subskrypcje 🔔
══════════════════
📊 /subskrypcja - Sprawdza stan Twojej subskrypcji.\n
```"""


def get_shortcuts_message() -> str:
    return """```🐐RanczoKlipy-Skróty_komend🐐
═════════════════════
📋 Skróty komend 📋
═════════════════════
🐐 /s, /start - Uruchamia główne menu.\n
🔎 /k, /klip - Wyszukuje klip na podstawie cytatu.\n
🔎 /sz, /szukaj - Wyszukuje klip na podstawie cytatu.\n
📋 /l, /lista - Wyświetla wszystkie klipy znalezione przez /szukaj.\n
✅ /w, /wybierz - Wybiera klip z listy uzyskanej przez /szukaj.\n
📺 /o, /odcinki - Wyświetla listę odcinków dla podanego sezonu.\n
✂️ /d, /dostosuj - Dostosowuje wybrany klip.\n
🎞️ /kom, /kompiluj - Tworzy kompilację klipów.\n
🔗 /pk, /polaczklipy - Łączy zapisane klipy w jeden.\n
🗑️ /uk, /usunklip - Usuwa zapisany klip.\n
📂 /mk, /mojeklipy - Wyświetla listę zapisanych klipów.\n
💾 /z, /zapisz - Zapisuje wybrany klip.\n
📤 /wys, /wyślij - Wysyła zapisany klip.\n
🐛 /r, /report - Raportuje błąd do administratora.\n
🔔 /sub, /subskrypcja - Sprawdza stan Twojej subskrypcji.\n
```"""


def get_invalid_command_message() -> str:
    return "❌ Niepoprawna komenda w menu startowym. Użyj /start, aby zobaczyć dostępne opcje. ❌"


def get_log_start_message_sent(username: str) -> str:
    return f"Start message sent to user '{username}'"


def get_log_received_start_command(username: str, content: str) -> str:
    return f"Received start command from user '{username}' with content: {content}"
