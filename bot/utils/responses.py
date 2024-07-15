from datetime import date
from typing import (
    Dict,
    List,
    Union,
)

import asyncpg
from tabulate import tabulate

number_to_emoji: Dict[str, str] = {
    '0': '0️⃣',
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣',
    '6': '6️⃣',
    '7': '7️⃣',
    '8': '8️⃣',
    '9': '9️⃣',
}


def convert_number_to_emoji(number: int) -> str:
    return ''.join(number_to_emoji.get(digit, digit) for digit in str(number))


def format_subscription_status_response(username: str, subscription_end: date, days_remaining: int) -> str:
    return f"""
✨ **Status Twojej subskrypcji** ✨

👤 **Użytkownik:** {username}
📅 **Data zakończenia:** {subscription_end}
⏳ **Pozostało dni:** {days_remaining}

Dzięki za wsparcie projektu! 🎉
"""


# fixme type hint
def format_myclips_response(clips, username) -> str:
    response = "🎬 Twoje Zapisane Klipy 🎬\n\n"
    response += f"🎥 Użytkownik: @{username}\n\n"
    clip_lines = []

    for idx, (clip_name, start_time, end_time, season, episode_number, is_compilation) in enumerate(clips, start=1):
        length = end_time - start_time if end_time and start_time is not None else None
        if length:
            minutes, seconds = divmod(length, 60)
            length_str = f"{minutes}m{seconds}s" if minutes else f"{seconds}s"
        else:
            length_str = "Brak danych"

        if is_compilation or season is None or episode_number is None:
            season_episode = "Kompilacja"
        else:
            episode_number_mod = (episode_number - 1) % 13 + 1
            season_episode = f"S{season:02d}E{episode_number_mod:02d}"

        emoji_index = convert_number_to_emoji(idx)
        line1 = f"{emoji_index} | 📺 {season_episode} | 🕒 {length_str}"
        line2 = f"👉 {clip_name}"
        clip_lines.append(f"{line1} \n{line2}")

    response += "```\n" + "\n\n".join(clip_lines) + "\n```"
    return response


# fixme type hint: jaki dict?
def format_episode_list_response(season: int, episodes: List[dict]) -> str:
    response = f"📃 Lista odcinków dla sezonu {season}:\n\n```\n"
    for episode in episodes:
        absolute_episode_number = episode['episode_number'] % 13
        if absolute_episode_number == 0:
            absolute_episode_number = 13
        formatted_viewership = f"{episode['viewership']:,}".replace(',', '.')

        response += f"🎬 {episode['title']}: S{season:02d}E{absolute_episode_number:02d} ({episode['episode_number']}) \n"
        response += f"📅 Data premiery: {episode['premiere_date']}\n"
        response += f"👀 Oglądalność: {formatted_viewership}\n\n"
    response += "```"
    return response


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


def get_admin_help_message() -> str:
    return """```🛠Instrukcje_dla_admina🛠

═════════════════════════════════
🔐 Zarządzanie użytkownikami: 🔐
═════════════════════════════════
➕ /addwhitelist <username> [is_admin=0] [is_moderator=0] [full_name] [email] [phone] - Dodaje użytkownika do whitelisty. Przykład: /addwhitelist johndoe 1 0 John Doe johndoe@example.com 123456789
➖ /removewhitelist <username> - Usuwa użytkownika z whitelisty. Przykład: /removewhitelist johndoe
✏️ /updatewhitelist <username> [is_admin] [is_moderator] [full_name] [email] [phone] - Aktualizuje dane użytkownika w whiteliście. Przykład: /updatewhitelist johndoe 0 1 John Doe johndoe@example.com 987654321
📃 /listwhitelist - Wyświetla listę wszystkich użytkowników w whiteliście.
📃 /listadmins - Wyświetla listę wszystkich adminów.
📃 /listmoderators - Wyświetla listę wszystkich moderatorów.

═════════════════════════════════
💳 Zarządzanie subskrypcjami: 💳
═════════════════════════════════
➕ /addsubscription <username> <days> - Dodaje subskrypcję użytkownikowi na określoną liczbę dni. Przykład: /addsubscription johndoe 30
🚫 /removesubscription <username> - Usuwa subskrypcję użytkownika. Przykład: /removesubscription johndoe

══════════════════════════════════
🔍 Zarządzanie transkrypcjami: 🔍
══════════════════════════════════
🔍 /transkrypcja <cytat> - Wyszukuje cytat w transkrypcjach i zwraca kontekst. Przykład: /transkrypcja Nie szkoda panu tego pięknego gabinetu?

```"""


def get_no_username_provided_message() -> str:
    return "✏️ Podaj nazwę użytkownika.✏️"


def get_user_added_message(username: str) -> str:
    return f"✅ Dodano {username} do whitelisty.✅"


def get_user_removed_message(username: str) -> str:
    return f"✅ Usunięto {username} z whitelisty.✅"


def get_user_updated_message(username: str) -> str:
    return f"✅ Zaktualizowano dane użytkownika {username}.✅"


def get_whitelist_empty_message() -> str:
    return "📭 Whitelist jest pusta.📭"


# fixme  tworzymy nowy folder "responses" i tam robimy np. delete_clip_responses.py dla kazdego handlera + generic wspoldzielone i WSZYSTKIE response'y mamy wyjebane do osobnych plikow i od razu wiadomo co zwraca ktory handler albo co jest wspoldzielone
def get_no_admins_found_message() -> str:
    return "📭 Nie znaleziono adminów.📭"


def get_no_moderators_found_message() -> str:
    return "📭 Nie znaleziono moderatorów.📭"


def get_subscription_extended_message(username: str, new_end_date: date) -> str:
    return f"✅ Subskrypcja dla użytkownika {username} przedłużona do {new_end_date}.✅"


def get_subscription_removed_message(username: str) -> str:
    return f"✅ Subskrypcja dla użytkownika {username} została usunięta.✅"


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


def get_users_string(users: List[asyncpg.Record]) -> str:
    return "\n".join([format_user(user) for user in users]) + "\n"


def format_user(user: asyncpg.Record) -> str:
    return (
        f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 "
        f"Phone: {user['phone']}"
    )


def create_whitelist_response(users: List[asyncpg.Record]) -> str:
    table = [["Username", "Full Name", "Email", "Phone", "Subskrypcja do"]]
    for user in users:
        table.append([user['username'], user['full_name'], user['email'], user['phone'], user['subscription_end']])

    response = f"```whitelista\n{tabulate(table, headers='firstrow', tablefmt='grid')}```"
    return response
