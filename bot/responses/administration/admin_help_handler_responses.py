def get_admin_help_message() -> str:
    return """```🛠Instrukcje_dla_admina🛠

═════════════════════════════════
🔐 Zarządzanie użytkownikami: 🔐
═════════════════════════════════
➕ /addwhitelist <id> - Dodaje użytkownika do whitelisty. Przykład: /addwhitelist 123456789
➖ /removewhitelist <id> - Usuwa użytkownika z whitelisty. Przykład: /removewhitelist 123456789
📃 /listwhitelist - Wyświetla listę wszystkich użytkowników w whiteliście.
📃 /listadmins - Wyświetla listę wszystkich adminów.
📃 /listmoderators - Wyświetla listę wszystkich moderatorów.
🔑 /klucz <key_content> - Zapisuje nowy klucz dla użytkownika. Przykład: /klucz some_secret_key
🔑 /listkey - Wyświetla listę wszystkich kluczy użytkowników.

═════════════════════════════════
💳 Zarządzanie subskrypcjami: 💳
═════════════════════════════════
➕ /addsubscription <id> <days> - Dodaje subskrypcję użytkownikowi na określoną liczbę dni. Przykład: /addsubscription 123456789 30
🚫 /removesubscription <id> - Usuwa subskrypcję użytkownika. Przykład: /removesubscription 123456789

══════════════════════════════════
🔍 Zarządzanie transkrypcjami: 🔍
══════════════════════════════════
🔍 /transkrypcja <cytat> - Wyszukuje cytat w transkrypcjach i zwraca kontekst. Przykład: /transkrypcja Nie szkoda panu tego pięknego gabinetu?

```"""


def get_message_sent_log_message(username: str) -> str:
    return f"Admin help message sent to user '{username}'."
