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


def get_message_sent_log_message(username: str) -> str:
    return f"Admin help message sent to user '{username}'."
